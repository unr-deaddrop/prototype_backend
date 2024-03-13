"""
The DeadDrop package manager.

Agents and protocol handlers come in .zip files that are in a standard format,
allowing the server to discover various metadata files that can be inspected
at runtime. Unless specified otherwise, the .zip files are called "bundles"
or "packaged" files; the resulting folder is "unpackaged" or simply a "package".

Agents and protocols are expected to provide a makefile with an `install` recipe
that allows for their metadata and any other install-specific files to be generated.
The package manager allows this metadata to be correctly discovered and parsed
on demand, serving as an interface between the package files at rest and the
Django models they correspond to.
"""

from pathlib import Path
import json
import logging
import os
import shutil
import stat
import subprocess
import zipfile

from backend.models import Agent, Protocol
from django.conf import settings

logger = logging.getLogger(__name__)

# As of right now, these are the files that are required to be present in unbundled
# packages. If any are missing, raise an exception.
#
# TODO: As of right now, the structure of these files are not validated.
# When we get deaddrop_meta set up, we'll probably implement validation at
# the same time. Since there's only one agent and its metadata is generated
# automatically, I'm not concerned about validation in the short term, but
# we should figure that out eventually.
REQUIRED_AGENT_METADATA_FILES = (
    "agent.json",
    "commands.json",
    "protocols.json",
)


def install_agent(bundle_path: Path) -> Agent:
    """
    Install an agent from a bundle.

    Returns the resulting instantiated agent, saving it to the database.
    """
    # Assert that the bundle path actually exists
    if not bundle_path.exists():
        raise RuntimeError(f"{bundle_path} does not exist!")

    # Decompress and move the package.
    package_path = decompress_and_move_package(
        bundle_path, Path(settings.AGENT_PACKAGE_DIR)
    )

    # Run the installation script to expose all the metadata. Currently, we don't
    # permit a custom script name, since that would require another layer of
    # expectations we don't really need to support right now.
    execute_install_script(package_path)

    # Assert that all of the (currently) required metadata files are there.
    if not check_required_metadata(package_path, REQUIRED_AGENT_METADATA_FILES):
        raise RuntimeError("Missing one or more required metadata files")

    # Copy the original bundle to the media directory in which agents are
    # being stored by manually constructing the path; see
    # - https://stackoverflow.com/questions/8332443/set-djangos-filefield-to-an-existing-file
    # - https://stackoverflow.com/questions/72418227/access-upload-to-of-a-models-filefield-in-django

    # Extract the agent name and version from the metadata, construct the package
    # name
    agent_name, agent_version = get_agent_info(package_path)
    internal_name = f"{agent_name}-{agent_version}"
    
    # Determine if an agent already exists with this name and version; if it exists,
    # invoke its delete function if it has no associated endpoints
    try:
        # Note that we only get one, since this comprises a unique set
        existing_agent = Agent.objects.get(name=agent_name, version=agent_version)
        
        if not existing_agent.endpoints.all().exists():
            # Permit the operation to continue.
            logger.warning(f"Overwriting installed agent {existing_agent}, it has no endpoints")
            existing_agent.delete()
        else:
            # Uh oh
            raise RuntimeError(
                f"This installation would overwrite {existing_agent}, which has"
                " endpoints associated with it"
            )
    except Agent.DoesNotExist:
        # No collision, no problem
        pass

    # Construct the effective final package directory; note that when we uploaded
    # the file to Django, it's a named temporary file; we'll rename it to what it's
    # supposed to be
    final_package_dir = package_path.with_name(internal_name)
    
    # If the package already exists, verify that it is not in use by any agents
    # (even if the package's name has somehow been modified, and therefore not 
    # caught by the prior agent check; this can also catch if the package
    # wasn't deleted even when the agent was)
    if final_package_dir.exists():
        try:
            using_agent = Agent.objects.get(package_path=str(final_package_dir))
        except Agent.DoesNotExist:
                # Blow it up
                logger.warning(f"Removing dangling package at {final_package_dir}")
                shutil.rmtree(final_package_dir, ignore_errors=True)
        
    try:
        os.rename(package_path, final_package_dir)
    except OSError:
        raise RuntimeError(
            f"The package is already installed at {final_package_dir} and is in use by {using_agent}!"
        )

    # Copy the original bundle to the media folder
    media_path = Path(Agent.package_file.field.upload_to) / Path(
        bundle_path.name
    ).with_stem(internal_name)
    bundle_target = Path(settings.MEDIA_ROOT) / media_path
    # Create the media folder if it doesn't already exist for any reason
    bundle_target.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy2(bundle_path, bundle_target)

    # Generate an Agent object, using the newly-stored media file as the
    # package_file field
    agent_obj = Agent(
        name=agent_name,
        version=agent_version,
        package_file=str(media_path),
        package_path=str(final_package_dir),
    )

    # Commit the Agent object to the database.
    agent_obj.save()

    # Return the resulting Agent.
    return agent_obj


def decompress_and_move_package(bundle_path: Path, package_base_path: Path) -> Path:
    """
    Given a path to a package file, decompress it into the target package directory.

    The bundle's name is used as the name of the decompression target. A path to
    the resulting folder is returned as the result. Note that it is not required
    that the bundle's name is the same as the underlying package's name, but it
    is required that it is unique relative to other installed packages.

    This raises RuntimeError if the target directory already exists.

    :param bundle_path: The path to the zipped package bundle to decompress.
    :param package_base_path: The base path containing all packages of a particular type.
    :return: The path to the root of the unbundled package.
    """
    # Determine where the unbundled packaged should go. In general, this is the
    # provided package path (which is likely either package/agents or
    # package/protocols) and then the package name.
    bundle_name = bundle_path.stem

    # Assert that the proposed base path exists.
    if not package_base_path.exists():
        raise RuntimeError(f"Package base path {package_base_path} does not exist!")

    # Assert that the new target path *does not* exist
    target_dir = package_base_path / Path(bundle_name)
    if target_dir.exists():
        raise RuntimeError(
            f"Target directory for package at {target_dir} already exists!"
        )

    # Unzip the package to the target directory; note that this also handles
    # the case in which the file isn't actually a zip file
    with zipfile.ZipFile(bundle_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    # Return the target directory
    return target_dir


def check_required_metadata(package_path: Path, required_files: tuple[str]) -> bool:
    """
    Check if all required metadata files are present in a particular package's
    directory.

    Returns True if the files are present, False if any are missing.
    """
    for filename in required_files:
        if not (package_path / Path(filename)).exists():
            logger.warning(
                f"{filename} missing during required metadata check for package rooted at {package_path}"
            )
            return False

    return True


def execute_install_script(
    package_path: Path, shell_command: str = "make install"
) -> None:
    """
    Execute the installation script provided with the package after unbundling.

    This simply executes `make install`. The install command can be overriden if
    necessary; shell=True is used to make shell utilities available.
    """
    # Execute the script in a shell - note this is intentionally blocking and
    # will raise an Exception on non-zero exit codes
    try:
        p = subprocess.run(
            shell_command, shell=True, capture_output=True, cwd=package_path
        )
        logger.info(p.stdout)
        if p.stderr:
            logger.warning(p.stderr)
    except subprocess.CalledProcessError as e:
        logger.exception(f"The install script failed! {p.stdout=} {p.stderr=}")
        raise e


def get_agent_info(package_path: Path) -> tuple[str, str]:
    """
    Get the internal name and version of an agent.

    This pulls from agent.json; if it does not exist, this raises RuntimeError.
    """
    target = package_path / "agent.json"
    if not target.exists():
        raise RuntimeError(f"agent.json missing from {package_path}")

    with open(target, "rt") as fp:
        data = json.load(fp)

    # TODO: in the future, this should be validated from deaddrop_meta and
    # the actual fields should be taken, not these magic dictionary keys
    return (data["name"], data["version"])
