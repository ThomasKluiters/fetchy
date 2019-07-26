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


def get_mirror(distribution=None):
    """Function to acquire mirror site

    For now it does not find the optimal mirror.
    """
    if distribution is None:
        distribution = get_distribution()
    extension = {"ubuntu": "com", "debian": "org"}[distribution]
    return f"http://ftp.{distribution}.{extension}/{distribution}/"


def get_ppa_url(ppa, distribution=None):
    """
    If a user supplies a ppa it might either be
    a URL pointing to the repository or a name of a
    ppa.

    If the user supplied a valid URL then we will simply
    use thise URL for the ppa.

    If the user supplied a name, then we will attempt to 
    construct a ppa url hosted on launchpad.
    """
    if validators.url(ppa):
        if not ppa.endswith("/"):
            return f"{ppa}/"
        return ppa

    if distribution is None:
        distribution = get_distribution()
    return f"http://ppa.launchpad.net/{ppa}/ppa/{distribution}/"


def get_fetchy_dir():
    """Function to acquire default fetchy dir

    Here the Packages list is stored.
    """
    home = str(Path.home())
    return os.path.join(home, ".fetchy")


def get_packages_file_location(
    fetchy_dir,
    distribution,
    distribution_version,
    architecture,
    repository,
    ppa=None,
    suffix=None,
):
    """Function to acquire package location

    Each Packages file is stored in a uniquely
    identifiable way.
    """
    base = f"{fetchy_dir}/Packages-{architecture}-{distribution}-{distribution_version}-{repository}"

    if suffix:
        base = base + "-" + suffix

    if ppa is not None:
        if validators.url(ppa):
            ppa = os.path.basename(ppa)
        return f"{base}-{ppa}"

    return base


def get_packages_control_file(
    distribution=None,
    distribution_version=None,
    architecture=None,
    mirror=None,
    repository=None,
    fetchy_dir=None,
    ppa=None,
    suffix=None,
):
    """Function to download (or get) the packages control file

    Here, all information can be optionally provided.

    The distribution is the distribution to target,
    optionally supplied (like `Debian` or `Ubuntu`).
    If none is supplied the current distribution is assumed.

    Architecture may also be optionally supplied and otherwise
    will be set to the architecture of the machine this
    script runs on.

    The mirror may also be supplied to a local mirror.

    If the file already exists then the file will not be downloaded.

    This function will then download the Packages control file
    into the fetchy directory. This directory defaults to `~/.fetchy`.
    """
    if distribution is None:
        distribution = get_distribution()

    if distribution_version is None:
        distribution_version = get_distribution_version()

    if architecture is None:
        architecture = get_architecture()

    if mirror is None:
        if ppa is not None:
            mirror = get_ppa_url(ppa, distribution)
        else:
            mirror = get_mirror(distribution)

    if fetchy_dir is None:
        fetchy_dir = get_fetchy_dir()

    packages_file = get_packages_file_location(
        fetchy_dir,
        distribution,
        distribution_version,
        architecture,
        repository,
        ppa,
        suffix,
    )

    logger.info(f"Using Package file {packages_file}")
    logger.info(f"Distribution: {distribution}, {distribution_version}")
    logger.info(f"Architecture: {architecture}")
    logger.info(f"Mirror: {mirror}")

    if not os.path.isdir(fetchy_dir):
        logger.warning(f"Fetchy directory does not exist, creating {fetchy_dir}")
        os.mkdir(fetchy_dir)

    if not os.path.isfile(packages_file):
        if suffix:
            packages_url = f"{mirror}dists/{distribution_version}-{suffix}/{repository}/binary-{architecture}/Packages.gz"
        else:
            packages_url = f"{mirror}dists/{distribution_version}/{repository}/binary-{architecture}/Packages.gz"

        packages_file_tar = packages_file + ".gz"

        logger.warning(f"Packages file does not exist, fetching {packages_url}")

        with tqdm(
            unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc="Downloading"
        ) as t:

            def hook(b=1, bsize=1, tsize=None):
                if tsize is not None:
                    t.total = tsize
                t.update(b * bsize - t.n)

            try:
                urllib.request.urlretrieve(packages_url, packages_file_tar, hook)
            except urllib.error.HTTPError as e:
                t.close()
                logger.error(
                    f"The combination of {distribution}, {distribution_version} and {architecture} does "
                    f"not seem to be valid. Is '{distribution_version}' a valid version of {distribution}?"
                )
                import sys

                sys.exit()

        with gzip.open(packages_file_tar, "rb") as data_in:
            with open(packages_file, "wb") as data_out:
                shutil.copyfileobj(data_in, data_out)

        os.remove(packages_file_tar)

    return Repository(packages_file, mirror)
