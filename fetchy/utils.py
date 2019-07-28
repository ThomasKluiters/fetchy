import os
import gzip
import urllib
import distro
import shutil
import platform
import logging
import validators

from tqdm import tqdm
from fetchy import Repository
from pathlib import Path

logger = logging.getLogger(__name__)

_known_versions = {
    "ubuntu": [
        "devel",
        "precise",
        "cosmic",
        "trusty",
        "xenial",
        "disco",
        "eoan",
        "bionic",
    ],
    "debian": [
        "buzz",
        "rex",
        "bo",
        "hamm",
        "slink",
        "potato",
        "woody",
        "sarge",
        "etch",
        "lenny",
        "squeeze",
        "wheezy",
        "jessie",
        "stretch",
        "buster",
        "bullseye",
        "sid",
    ],
}


def gather_exclusions(exclusions):
    """
    Gathers a list of dependencies that should be excluded.

    Exclusion values ending with a .txt extension will be
    parsed as files and will read these files line by line.
    """
    dependencies_to_exclude = []

    for exclusion in exclusions:
        if exclusion.endswith(".txt"):
            with open(exclusion, "r") as exclusion_file:
                for exclusion_line in exclusion_file:
                    dependencies_to_exclude.append(exclusion_line.strip())

        else:
            dependencies_to_exclude.append(exclusion)

    return dependencies_to_exclude


def is_os_supported(distribution=None):
    if distribution is None:
        distribution = distro.id()
    return distribution in ["debian", "ubuntu"]


def is_version_supported(distribution, version):
    if not is_os_supported(distribution=distribution):
        return False
    return version in _known_versions[distribution]


def get_supported_versions_for(distribution):
    return reversed(_known_versions[distribution])


def get_distribution():
    """Function to acquire current Distribution

    This function will return the current distribution
    if the user is running on a Linux machine.
    """
    return distro.id()


def get_distribution_version():
    """
    Function to acquire current Distribution Version

    This function will return the current distribution version
    if the user is running on a Linux machine.
    """
    return distro.codename()


def get_architecture():
    """Function to acquire machine architecture

    For now let's make some simple assumptions that 64bit -> amd64.
    """
    (arch, _) = platform.architecture()
    mapping = {"64bit": "amd64", "32bit": "i386"}
    if arch not in mapping:
        logger.error(
            f"{arch} is not recognized. Please specify the architecture you want to use (e.g. --architecture amd64)."
        )
    return mapping[arch]
