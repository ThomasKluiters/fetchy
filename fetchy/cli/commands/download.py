from .command import FetchyPackageCommand


class DownloadCommand(FetchyPackageCommand):
    """
    Download a list of packages.

    download
      {packages*        : the list of packages to download}
      {--o|out=         : If set, the directory in which the packages will be downloaded (e.g. `my-packages`)}
    """

    def handle(self):
        self.update_config()

        packages = self.argument("packages")

        out_dir = "packages"
        if self.option("out"):
            out_dir = self.option("out")

        self.fetchy.download_packages(out_dir, packages)
