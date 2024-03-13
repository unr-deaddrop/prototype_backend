"""
The DeadDrop payload generation system.

The payload generation system works by assuming that a package contains a
`make payload_entry` recipe that expects the existence of a `build-config.json`.

The following conventions are assumed:
- That a Makefile exists, and that a payload_entry recipe exists;
- That the script uses a JSON file at the root of the agent directory called
  build-config.json that is used, partially or in full, to configure the agent;
- That once the script returns, the following contents are made available in
  the temporary directory:
  - agent_cfg.json, the final JSON configuration document to be stored with
    the agent and used in any communications (which is identical in structure,
    but not necessarily values, to the original JSON passed in);
  - payload.zip, the compiled or bundled payload that is intended to be delivered
    and executed on a target device;
  - payload-logs.txt, a standard text file containing the payload log output
    (which is used to generate a single giant Log entry associated with this task).

In general, it is assumed that the payload_entry recipe will leverage a
docker-compose-payload.yml and a corresponding Dockerfile.payload. These
are required for platform-independent payload construction, though not enforced
by the package manager (only the existence of a Makefile is checked).

Note that unlike the package manager, this module *does* import the Django
models, as I currently don't see any reason for this module to ever be imported
by the Django models. The advantage of strictly tying these to the models is that
we can keep the interface between agents and the server consistent.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from tempfile import TemporaryDirectory
import json
import logging
import os
import shutil
import subprocess
import uuid

logger = logging.getLogger(__name__)

from django.contrib.auth.models import User
from django.conf import settings
from backend.models import Endpoint, Log, Agent
from django_celery_results.models import TaskResult

from deaddrop_meta.protocol_lib import DeadDropLogLevel

AGENT_CFG_FILE_NAME = "agent_cfg.json"
PAYLOAD_FILE_NAME = "payload.zip"
LOG_FILE_NAME = "payload-logs.txt"


def build_payload(
    agent: Agent,
    build_args: dict[str, Any],
    task_id: Optional[str],
    user: Optional[User],
    **kwargs,
) -> Endpoint:
    """
    Build a new payload from a package, provided a set of validated
    build arguments.

    This returns the newly-instantiated Endpoint using the provided Agent
    instance as the template and the build arguments provided. Note that the
    agent's build system may choose to overwrite these build arguments at will.

    The new payload is set as the FileField for the new Endpoint instance. Note
    that all build outputs are included with the payload itself; it is your
    responsibility to determine what to send to the target from the actual
    payload bundle.

    If the build fails, as measured by either a failing build script call or
    the absence of `payload.zip`, this raises RuntimeException.

    :param model_data: The serialized data from the payload generation endpoint.
    :param agent: The actual agent to generate the payload from.
    :param task_id: The task ID to associate logs with, if set.
    :param user: The user to associate logs with, if set.
    :param kwargs: Any other data to pass to the Endpoint constructor.
    :returns: A new Endpoint instance.
    """
    # Copy the entire package into a temporary directory (note that we don't need
    # to resolve the package path, since it's already correct relative to wherever
    # Django and the workers are running)
    temp_dir = TemporaryDirectory()

    if not Path(agent.package_path).exists():
        raise RuntimeError(
            f"The package at {Path(agent.package_path).resolve()} does not exist!"
        )

    shutil.copytree(agent.package_path, temp_dir.name, dirs_exist_ok=True)
    temp_dir_path = Path(temp_dir.name).resolve()
    logger.info(f"Using {temp_dir_path} for build")

    # Convert the build arguments into a JSON file, writing it as build-config.json
    # into the temporary directory
    with open(temp_dir_path / "build_config.json", "wt+") as fp:
        json.dump(build_args, fp)

    # Assert that the script is present in our temporary directory, then call it
    target = temp_dir_path / "Makefile"
    if not target.exists():
        raise RuntimeError(
            f"The payload build script {target} is missing from {temp_dir_path}!"
        )
    p = subprocess.run(
        ["make", "payload_entry"], shell=False, capture_output=True, cwd=temp_dir_path
    )
    logger.warning(p.stdout)

    # Take payload-logs.txt and convert it into a single LogMessage (this is
    # first so that even if the rest of the build fails, we have a coherent
    # log message)
    get_and_save_build_log(temp_dir_path, user, task_id)

    # Deserialize agent_cfg.json and turn it back into a Python dictionary,
    # then retrieve the agent ID from the dictionary
    build_cfg = get_build_cfg_json_as_dict(temp_dir_path)
    agent_id = uuid.UUID(build_cfg["agent_config"]["AGENT_ID"])

    # Copy payload.zip into Django's media folder (creating it if it doesn't
    # already exist) - do this last so that we don't have dangling payloads
    media_path = get_payload_and_copy(temp_dir_path, agent_id, agent)

    # Create and save a new Endpoint instance
    # If we've made it this far, we're going to be overwriting any user-supplied
    # payload file since this is clearly a new endpoint.
    kwargs.pop("payload_file")
    # Connections are disallowed when creating new physical endpoints.
    kwargs.pop("connections")

    endpoint = Endpoint(
        id=agent_id,
        agent=agent,
        agent_cfg=build_cfg,
        payload_file=str(media_path),
        **kwargs,
    )
    endpoint.save()

    # Return the build result
    return endpoint


def get_and_save_build_log(
    build_dir: Path, user: Optional[User], task_id: Optional[str]
) -> Log:
    log_path = build_dir / LOG_FILE_NAME

    if not log_path.exists():
        raise RuntimeError(f"Missing log output for payload at {log_path}!")
    with open(log_path, "rt") as fp:
        logger.debug(f"Creating log entry from data at {log_path}")
        log = Log(
            source=None,
            user=user,
            task=TaskResult.objects.get(task_id=task_id),
            category="payload-build",
            level=DeadDropLogLevel.INFO,
            timestamp=datetime.now(),
            data=fp.read(),
        )

    log.save()

    return log


def get_build_cfg_json_as_dict(build_dir: Path) -> dict[str, Any]:
    agent_cfg_path = build_dir / AGENT_CFG_FILE_NAME

    # Deserialize agent_cfg.json and turn it back into a Python dictionary
    if not agent_cfg_path.exists():
        raise RuntimeError(f"Missing final agent configuration from {agent_cfg_path}!")
    with open(agent_cfg_path, "rt") as fp:
        return json.load(fp)


def get_payload_and_copy(build_dir: Path, agent_id: uuid.UUID, agent: Agent) -> Path:
    """
    Copy the payload to the appropriate media folder.

    Return the path to the payload, relative to the media folder.
    """
    payload_path = build_dir / PAYLOAD_FILE_NAME

    # Copy payload.zip into Django's media folder (creating it if it doesn't
    # already exist) - do this last so that we don't have dangling payloads
    if not payload_path.exists():
        raise RuntimeError(f"Missing payload from {payload_path}!")

    media_path = (
        Path(Endpoint.payload_file.field.upload_to) / f"{str(agent)}-{agent_id}.zip"
    )
    bundle_target = Path(settings.MEDIA_ROOT) / media_path

    # Create the media folder if it doesn't already exist for any reason, then copy
    bundle_target.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(payload_path, bundle_target)

    return media_path
