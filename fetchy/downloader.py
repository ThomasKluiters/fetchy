import os
import logging
import urllib.request

from tqdm import tqdm

logger = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, packages, mirror=None, out_dir="./out"):
        """A Downloader Object

        The Downloader class is responsible for
        downloading packages and it's dependencies.
        """
        self.packages = packages
        self.mirror = mirror
        self.out_dir = out_dir

    def download_package(self, package_name, version=None, architecture=None):
        """Function for downloading a package

        This function downloads the specified
        package name with the supplied version
        and architecture when given.

        Furthermore, all dependencies for the
        package are also downloaded.
        """
        if not os.path.isdir(self.out_dir):
            logger.info(f"Creating output directory {self.out_dir}")
            os.mkdir(self.out_dir)

        logger.info(f"Gathering dependencies for {package_name}")
        for (name, package) in self.gather_dependencies(package_name).items():
            package_url = f"{self.mirror}/{package.file_name()}"
            package_file = f"{self.out_dir}/{name}-{package.version}.deb"

            logger.info(f"Downloading package {name} at {package_url}")

            with tqdm(
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                miniters=1,
                desc=f"Downloading {name}",
            ) as t:

                def hook(b=1, bsize=1, tsize=None):
                    if tsize is not None:
                        t.total = tsize
                    t.update(b * bsize - t.n)

                urllib.request.urlretrieve(package_url, package_file, hook)

    def gather_dependencies(self, package_name):
        """Function for gathering dependencies

        This function will naaively gather
        dependencies for the given package.

        This will only gather Depends and
        Pre-Depends dependencies.
        """
        queue = [package_name]

        dependencies = {}

        while queue:
            _package_name = queue.pop()

            package = self.packages[_package_name]

            dependencies[_package_name] = package

            for dependency in package.dependencies:
                if dependency.name not in dependencies:
                    queue.append(dependency.name)

            for pre_dependency in package.pre_dependencies:
                if pre_dependency.name not in dependencies:
                    queue.append(pre_dependency.name)

        return dependencies
