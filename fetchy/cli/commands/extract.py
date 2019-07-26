from .command import FetchyPackageCommand


class ExtractCommand(FetchyPackageCommand):
    """
    Extract packages files into a directory.

    extract
      {packages*        : the list of packages to extract}
      {--o|out=         : If set, the directory in which the packages will be extracted (e.g. `my-packages`)}
    """

    def handle(self):
        self.update_config()

        packages = self.argument("packages")

        out_dir = "extracted-" + "-".join(packages)
        if self.option("out"):
            out_dir = self.option("out")

        self.fetchy.extract_packages(out_dir, packages)
