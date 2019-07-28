from .command import FetchyPackageCommand


class DockerizeCommand(FetchyPackageCommand):
    """
    Dockerize packages into a docker image.

    dockerize
      {packages*        : the list of packages to dockerize}
      {--t|tag=         : If set, the tag to use for the docker images (e.g. `my-image`)}
      {--b|base=        : If set, the base image to use for the docker image}
    """

    def handle(self):
        self.update_config()

        packages = self.argument("packages")

        tag = "-".join(packages) + "-image"
        if self.option("tag"):
            tag = self.option("tag")

        base = "scratch"
        if self.option("base"):
            base = self.option("base")

        image = self.fetchy.dockerize_packages(tag, packages, base)

        self.line(f"Succesfully built image: `{image}`!")
