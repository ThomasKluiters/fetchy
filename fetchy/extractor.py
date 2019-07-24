import os
import tarfile
import unix_ar as arfile

from tqdm import tqdm


class Extractor(object):
    def __init__(self, root="./fs"):
        """
        The extractor will unpack packages into their directory structure.
        """
        self.root = root

    def extract(self, package_path):
        """
        Extract a single debian package into the specified root directory.
        """
        package_file = arfile.open(package_path)
        with package_file.open("data.tar.xz") as tar_ball:
            with tarfile.open(fileobj=tar_ball) as tar_file:
                tar_file.extractall(self.root)
        package_file.close()

    def extract_all(self, packages_files):
        """
        Extracts all debian packages given as an argument.
        """
        with tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=len(packages_files),
            miniters=1,
            desc=f"Extracting packages...",
        ) as t:
            for package_file in packages_files:
                self.extract(package_file)
                t.update(1)
