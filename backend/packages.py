"""
The DeadDrop package manager.

Agents and protocol handlers come in .zip files that are in a standard format,
allowing the server to discover various metadata files that can be inspected
at runtime. Unless specified otherwise, the .zip files are called "bundles"
or "packaged" files; the resulting folder is "unpackaged" or simply a "package".

Agents and protocols are expected to provide an install.sh or install.bat script
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

# I have no idea lol
REQUIRED_PROTOCOL_METADATA_FILES = ("protocol.json",)


def install_agent(bundle_path: Path) -> Agent:
    """
    Install an agent from a bundle.

    Returns the resulting instantiated agent, saving it to the database.
    """
    # Assert that the bundle path actually exists
    if not bundle_path.exists():
        raise RuntimeError(f"{bundle_path} does not exist!")
    
    # Decompress and move the package.
    package_path = decompress_and_move_package(bundle_path, Path(settings.AGENT_PACKAGE_DIR))

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
    
    # Construct the effective final package directory; note that when we uploaded
    # the file to Django, it's a named temporary file; we'll rename it to what it's
    # supposed to be
    final_package_dir = package_path.with_name(internal_name)
    try:
        os.rename(package_path, final_package_dir)
    except OSError:
        raise RuntimeError(f"The package seems to already be installed at {final_package_dir}!")
    
    # Copy the original bundle to the media folder
    media_path = Path(Agent.package_file.field.upload_to) / Path(bundle_path.name).with_stem(internal_name)
    bundle_target = Path(settings.MEDIA_ROOT) / media_path
    # Create the media folder if it doesn't already exist for any reason
    bundle_target.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy2(bundle_path, bundle_target)

    # Generate an Agent object, using the newly-stored media file as the 
    # package_file field
    agent_obj = Agent(
        name = agent_name,
        version = agent_version,
        package_file = str(media_path),
        package_path = str(final_package_dir)
    )

    # Commit the Agent object to the database.
    agent_obj.save()

    # Return the resulting Agent.
    return agent_obj

def install_protocol(bundle_path: Path) -> Protocol:
    """
    Install a protocol from a bundle.

    Returns the resulting instantiated protocol, saving it to the database.
    """
    # Assert that the bundle path actually exists
    if not bundle_path.exists():
        raise RuntimeError(f"{bundle_path} does not exist!")
    
    # Decompress and move the package.

    # Run the installation script to expose all the metadata.

    # Assert that all of the (currently) required metadata files are there.

    # Generate a Protocol object

    # Commit the Protocol object to the database.

    # Return the resulting Protocol.
    raise NotImplementedError


def decompress_and_move_package(
    bundle_path: Path, package_base_path: Path
) -> Path:
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
    target_dir = package_base_path/Path(bundle_name)
    if target_dir.exists():
        raise RuntimeError(f"Target directory for package at {target_dir} already exists!")

    # Unzip the package to the target directory; note that this also handles
    # the case in which the file isn't actually a zip file
    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
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
        if not (package_path/Path(filename)).exists():
            logger.warning(f"{filename} missing during required metadata check for package rooted at {package_path}")
            return False

    return True

def execute_install_script(package_path: Path, script_name: str = "") -> None:
    """
    Execute the installation script provided with the package after unbundling.

    For Windows machines (as determined by `os.name`), this executes `install.bat`
    by default. For Linux machines, this executes `install.sh` after marking
    the file as executable *for the current user*.

    The install script's location can be overriden with `script_name` if necessary.
    """
    # If no script name was provided, use the platform-dependent defaults;
    # assume POSIX unless stated otherwise
    if not script_name:
        if os.name == "posix":
            script_name = 'install.sh'
        if os.name == 'nt':
            script_name = "install.bat"
        
    # Assert that the script is present at the proposed location
    script_path = package_path / Path(script_name)
    if not script_path.exists():
        raise RuntimeError(f"Install script {script_name} does not exist at {script_path.resolve()}")

    # Mark the script as executable (this does nothing on Windows)
    # - https://stackoverflow.com/questions/16249440/changing-file-permission-in-python
    # - https://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python/55591471#55591471
    st = os.stat(script_path)
    os.chmod(script_path, st.st_mode | stat.S_IEXEC)

    # Execute the script in a shell - note this is intentionally blocking and
    # will raise an Exception on non-zero exit codes
    try:
        p = subprocess.run(script_path.resolve(), shell=False, capture_output=True, cwd=package_path)
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
    return (data['name'], data['version'])
