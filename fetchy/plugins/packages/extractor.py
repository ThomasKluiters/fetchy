import os
import tarfile
import unix_ar as arfile

from tqdm import tqdm


class Extractor(object):
    def __init__(self, root):
        """
        The extractor will unpack packages into their directory structure.
        """
        self.root = root

    def extract_tar_file(self, package_path):
        """
        Extract a single debian package into the specified root directory.
        """
        package_file = arfile.open(package_path)
        for info in package_file.infolist():
            if info.name.decode().startswith("data.tar"):
                with package_file.open(info.name.decode()) as tar_ball:
                    with tarfile.open(fileobj=tar_ball) as tar_file:
                        tar_file.extractall(self.root)
        package_file.close()

    def extract_all(self, packages_files):
        """
        Extracts all debian packages given as an argument.
        """
        with tqdm(total=len(packages_files), desc=f"Extracting packages...") as t:
            for package_file in packages_files:
                self.extract_tar_file(package_file)
                t.update(1)
