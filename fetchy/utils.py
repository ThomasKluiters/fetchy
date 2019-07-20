import os
import gzip
import urllib
import shutil
import platform
import logging

from tqdm import tqdm

logger = logging.getLogger(__name__)

def get_distribution():
    """Function to acquire current Distribution

    This function will return the current distribution
    if the user is running on a Linux machine.
    """
    (distribution, _, _) = platform.linux_distribution()
    return distribution.lower()


def get_distribution_version():
    """Function to acquire current Distribution Version

    This function will return the current distribution version
    if the user is running on a Linux machine.
    """
    (_, _, distribution_version) = platform.linux_distribution()
    return distribution_version.lower()


def get_architecture():
    """Function to acquire machine architecture

    For now let's make some simple assumptions that 64bit -> amd64.
    """
    (arch, _) = platform.architecture()
    return {"64bit": "amd64"}[arch]


def get_mirror(distribution):
    """Function to acquire mirror site

    For now it does not find the optimal mirror.
    """
    extension = {"ubuntu": "com", "debian": "org"}[distribution]
    return f"http://ftp.{distribution}.{extension}/{distribution}/"


def get_fetchy_dir():
    """Function to acquire default fetchy dir

    Here the Packages list is stored.
    """
    home = os.path.expanduser("~")
    return f"{home}/.fetchy"


def get_packages_file_location(
    fetchy_dir, distribution, distribution_version, architecture
):
    """Function to acquire package location

    Each Packages file is stored in a uniquely
    identifiable way.
    """
    return f"{fetchy_dir}/Packages-{architecture}-{distribution}-{distribution_version}"


def get_packages_control_file(
    distribution=None,
    distribution_version=None,
    architecture=None,
    mirror=None,
    fetchy_dir=None,
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
        mirror = get_mirror(distribution)

    if fetchy_dir is None:
        fetchy_dir = get_fetchy_dir()

    packages_file = get_packages_file_location(
        fetchy_dir, distribution, distribution_version, architecture
    )

    logger.info(f"Using Package file {packages_file}")
    logger.info(f"Distribution: {distribution}, {distribution_version}")
    logger.info(f"Architecture: {architecture}")
    logger.info(f"Mirror: {mirror}")

    if not os.path.isdir(fetchy_dir):
        logger.warning(f"Fetchy directory does not exist, creating {fetchy_dir}")
        os.mkdir(fetchy_dir)

    if not os.path.isfile(packages_file):
        packages_url = f"{mirror}dists/{distribution_version}/main/binary-{architecture}/Packages.gz"
        packages_file_tar = packages_file + ".gz"

        logger.warning(f"Packages file does not exist, fetching {packages_url}")

        with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc="Downloading") as t:
            def hook(b=1, bsize=1, tsize=None):
                if tsize is not None:
                    t.total = tsize
                t.update(b * bsize - t.n)
            urllib.request.urlretrieve(packages_url, packages_file_tar, hook)

        with gzip.open(packages_file_tar, "rb") as data_in:
            with open(packages_file, "wb") as data_out:
                shutil.copyfileobj(data_in, data_out)

        os.remove(packages_file_tar)

    return packages_file