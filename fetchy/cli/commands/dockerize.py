from .command import FetchyPackageCommand


class DockerizeCommand(FetchyPackageCommand):
    """
    Dockerize packages into a docker image.

    dockerize
      {packages*        : the list of packages to dockerize}
      {--t|tag=         : If set, the tag to use for the docker images (e.g. `my-image`)}
    """

    def handle(self):
        self.update_config()

        packages = self.argument("packages")

        tag = "-".join(packages) + "-image"
        if self.option("tag"):
            tag = self.option("tag")

        self.fetchy.dockerize_packages(tag, packages)
