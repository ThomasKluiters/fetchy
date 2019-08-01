from .command import FetchyCommandBase

from PyInquirer import prompt

from fetchy import (
    is_os_supported,
    is_version_supported,
    get_architecture,
    get_distribution,
    get_distribution_version,
    get_supported_versions_for,
)

import yaml


class DockerizeCommand(FetchyCommandBase):
    """
    Dockerize packages into a docker image.

    dockerize
      {packages*        : the list of packages to dockerize}
      {--B|blueprint    : If set, will output a yaml file of the blueprint}
      {--t|tag=         : If set, the tag to use for the docker images (e.g. `my-image`)}
      {--b|base=        : If set, the base image to use for the docker image}
      {--d|distribution= : If set, the distribution to use when searching for packages (e.g. `ubuntu`)}
      {--c|codename=     : If set, the codename (version) of the distribution version to use when searching for packages (e.g. `bionic`)}
      {--a|architecture= : If set, the architecture to use when searching for packages (e.g. `amd64`)}
      {--p|ppa=*         : If set, either name(s) or URL(s) pointing to Personal Package Archive(s).}
      {--e|exclude=*     : If set, either name(s) or path(s) of packages to exclude. If a path is given a file is given
              then the extension if this file should be .txt and contain, on each line, a package to exclude.}
    """

    def get_or_default(self, name, default):
        if self.option(name) is not None:
            return self.option(name)
        return default

    def handle(self):
        options = self.option(None)

        configuration = {
            "distribution": self.get_or_default("distribution", get_distribution()),
            "codename": self.get_or_default("codename", get_distribution_version()),
            "architecture": self.get_or_default("architecture", get_architecture()),
            "base": self.get_or_default("base", "scratch"),
            "tag": self.get_or_default("tag", "-".join(self.argument("packages"))),
            "packages": {
                "fetch": self.argument("packages"),
                "exclude": options["exclude"],
                "ppa": options["ppa"],
            },
        }

        self._validate_configuration(configuration)

        if self.option("blueprint"):
            with open("blueprint.yml", "w") as file:
                yaml.dump(configuration, file)

        result = self.fetchy.blueprint_from_dict(configuration).dockerize()

        self.line(f"Successfully built {result['tag']}")

    def _validate_configuration(self, configuration):
        if not is_os_supported(configuration["distribution"]):
            message = (
                "Sorry, currently we do not support packages indices that are "
                "running on your current operating system. Please select an operating system "
                "you'd like to use to search packages for:"
            )
            configuration["distribution"] = prompt(
                [
                    {
                        "type": "list",
                        "message": message,
                        "name": "distribution",
                        "choices": ["ubuntu", "debian"],
                    }
                ]
            )["distribution"]
        if not is_version_supported(
            configuration["distribution"], configuration["codename"]
        ):
            message = (
                f"Sorry, the codename '{configuration['codename']}' is not recognised by fetchy for "
                f"the distribution {configuration['distribution']}. Please select a codename for which "
                "you'd like to search packages for:"
            )
            configuration["codename"] = prompt(
                [
                    {
                        "type": "list",
                        "message": message,
                        "name": "codename",
                        "choices": get_supported_versions_for(
                            configuration["distribution"]
                        ),
                    }
                ]
            )["codename"]
