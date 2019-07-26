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

    def extract_tar_file(self, package_path):
        """
        Extract a single debian package into the specified root directory.
        """
        try:
            package_file = arfile.open(package_path)
            for info in package_file.infolist():
                if info.name.decode().startswith("data.tar"):
                    with package_file.open(info.name.decode()) as tar_ball:
                        with tarfile.open(fileobj=tar_ball) as tar_file:
                            tar_file.extractall(self.root)
                            return self.extract_binary_paths(tar_file)
        finally:
            package_file.close()

    def extract_binary_paths(self, tar_file):
        """
        Find binaries for a specific package.
        """
        return set(
            [name.lstrip(":") for name in tar_file.getnames() if name.endswith("/bin")]
        )

    def extract_all(self, packages_files):
        """
        Extracts all debian packages given as an argument.
        """
        binaries = set(["/bin", "/usr/bin"])

        with tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=len(packages_files),
            miniters=1,
            desc=f"Extracting packages...",
        ) as t:
            for package_file in packages_files:
                paths = self.extract_tar_file(package_file)
                binaries.update(paths)
                t.update(1)
        return binaries
