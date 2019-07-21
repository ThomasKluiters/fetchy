import os
import logging
import urllib.request

from tqdm import tqdm

logger = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, packages, out_dir="./out"):
        """
        The Downloader class is responsible for downloading packages and it's dependencies.

        Parameters
        ----------
        packages : a dictionary containing a collection of packages this
            Downloader may use to satisfy dependencies.

        out_dir : the output directory this Downloader will download packages
            into.
        """
        self.packages = packages
        self.out_dir = out_dir

    def download_package(self, package_name, version=None):
        """
        Downloads a package and its' dependencies into a folder.

        Before downloading any package, the dependencies of the given
        package are first gathered into a list of dependencies.

        Then, once all dependencies are determined, each dependency
        is downloaded into the folder this Downloader has been configured
        to use as an output directory.

        Parameters
        ----------
        package_name : string representing the name of the package
            that should be downloaded.
        """
        if not os.path.isdir(self.out_dir):
            logger.info(f"Creating output directory {self.out_dir}")
            os.mkdir(self.out_dir)

        logger.info(f"Gathering dependencies for {package_name}")
        for (name, package) in self.gather_dependencies(package_name).items():
            package_file = f"{self.out_dir}/{os.path.basename(package.file_name())}"
            package_url = package.download_url()

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

    def gather_dependencies(self, package_names):
        """
        Gather dependencies for a package.

        This function will naaively gather dependencies for the given package name.

        This will only gather Depends and Pre-Depends dependencies and thus only gather
        the dependencies that are required in order to make the given package run.

        Parameters
        ----------
        package_name : string representing the name of the package
            dependencies should be gathereed for.
        
        Returns
        -------
        dict
            A dictionary containing all the dependencies required for
            the given package. Each dependency is stored as a Package
            object and uses the package name as key.
        """
        if isinstance(package_names, str):
            package_names = [package_names]

        queue = package_names

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
