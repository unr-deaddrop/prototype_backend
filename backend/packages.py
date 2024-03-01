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

from backend.models import Agent, Protocol

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
    # Decompress and move the package.

    # Run the installation script to expose all the metadata.

    # Assert that all of the (currently) required metadata files are there.

    # Generate an Agent object

    # Commit the Agent object to the database.

    # Return the resulting Agent.
    raise NotImplementedError


def install_protocol(bundle_path: Path) -> Protocol:
    """
    Install a protocol from a bundle.

    Returns the resulting instantiated protocol, saving it to the database.
    """
    # Decompress and move the package.

    # Run the installation script to expose all the metadata.

    # Assert that all of the (currently) required metadata files are there.

    # Generate a Protocol object

    # Commit the Protocol object to the database.

    # Return the resulting Protocol.
    raise NotImplementedError


def decompress_and_move_package(
    bundle_path: Path, package_base_path: Path, package_name: str
):
    """
    Given a path to a package file, decompress it into the target package directory.

    :param bundle_path: The path to the zipped package bundle to decompress.
    :param package_base_path: The base path containing all packages of a particular type.
    :param package_name: The name of the package, used as the target folder relative
        to `package_path`.
    """
    # Determine where the unbundled packaged should go. In general, this is the
    # provided package path (which is likely either package/agents or
    # package/protocols) and then the package name.

    # Unzip the package to the target directory
    raise NotImplementedError


def check_required_metadata(package_path: Path, required_files: tuple[str]) -> bool:
    """
    Check if all required metadata files are present in a particular package's
    directory.

    Returns True if the files are present, False if any are missing.
    """
    raise NotImplementedError


def execute_install_script(package_path: Path, script_name: str = "") -> None:
    """
    Execute the installation script provided with the package after unbundling.

    For Windows machines (as determined by `os.name`), this executes `install.bat`
    by default. For Linux machines, this executes `install.sh` after marking
    the file as executable *for the current user*.

    The install script's location can be overriden with `script_name` if necessary.
    """
    # If no script name was provided, use the platform-dependent defaults

    # Assert that the script is present at the proposed location

    # If Linux is in use, mark the script as executable

    # Execute the script in a shell
    raise NotImplementedError
