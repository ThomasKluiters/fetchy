from cleo import Command

from PyInquirer import prompt

from fetchy import (
    is_os_supported,
    is_version_supported,
    get_supported_versions_for,
    config_from_env,
)


class FetchyCommandBase(Command):
    @property
    def fetchy(self):
        return self.application.fetchy


class FetchyPackageCommand(FetchyCommandBase):
    """
      {--d|distribution= : If set, the distribution to use when searching for packages (e.g. `ubuntu`)}
      {--c|codename=     : If set, the codename (version) of the distribution version to use when searching for packages (e.g. `bionic`)}
      {--a|architecture= : If set, the architecture to use when searching for packages (e.g. `amd64`)}
      {--p|ppa=*         : If set, either name(s) or URL(s) pointing to Personal Package Archive(s).}
      {--e|exclude=*     : If set, either name(s) or path(s) of packages to exclude. If a path is given a file is given
              then the extension if this file should be .txt and contain, on each line, a package to exclude.}
    """

    def __init__(self):
        self.__doc__ = self.__doc__ + FetchyPackageCommand.__doc__
        super(FetchyPackageCommand, self).__init__()

    def update_config(self):
        self._populate_config()
        self._validate_config()

    def _populate_config(self):
        if self.option("exclude"):
            self.fetchy.config.update("_exclusions", self.option("exclude"))

        if self.option("distribution"):
            self.fetchy.config.update("distribution", self.option("distribution"))

        if self.option("codename"):
            self.fetchy.config.update("version", self.option("codename"))

        if self.option("architecture"):
            self.fetchy.config.update("architecture", self.option("distribution"))

        if self.option("ppa"):
            self.fetchy.config.update("ppas", self.option("ppa"))

    def _validate_config(self):
        if not is_os_supported(self.fetchy.config.distribution):
            message = (
                "Sorry, currently we do not support packages indices that are "
                "running on your current operating system. Please select an operating system "
                "you'd like to use to search packages for:"
            )
            self.fetchy.config.update(
                "distribution",
                prompt(
                    [
                        {
                            "type": "list",
                            "message": message,
                            "name": "distribution",
                            "choices": ["ubuntu", "debian"],
                        }
                    ]
                )["distribution"],
            )
        if not is_version_supported(
            self.fetchy.config.distribution, self.fetchy.config.version
        ):
            message = (
                f"Sorry, the version {self.fetchy.config.version} is not recognised by fetchy for "
                f"the distribution {self.fetchy.config.distribution}. Please select a version for which "
                "you'd like to search packages for:"
            )

            self.fetchy.config.update(
                "version",
                prompt(
                    [
                        {
                            "type": "list",
                            "message": message,
                            "name": "version",
                            "choices": get_supported_versions_for(
                                self.fetchy.config.distribution
                            ),
                        }
                    ]
                )["version"],
            )
