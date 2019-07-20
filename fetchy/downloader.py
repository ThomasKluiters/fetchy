import urllib.request


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

        for (name, package) in self.gather_dependencies(package_name).items():
            print(f"Downloading {name}")

            url = f"{self.mirror}/{package.file_name()}"
            file_name = f"{self.out_dir}/{name}-{package.version}.deb"

            urllib.request.urlretrieve(url, file_name)

    def gather_dependencies(self, package_name):
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
