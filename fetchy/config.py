from fetchy import (
    get_architecture,
    get_distribution,
    get_distribution_version,
    gather_exclusions,
)


def config_from_env():
    return FetchyConfig(
        get_distribution(), get_distribution_version(), get_architecture()
    )


class FetchyConfig(object):
    def __init__(
        self,
        distribution=None,
        codename=None,
        architecture=None,
        ppas=None,
        exclusions=None,
    ):
        self.distribution = distribution
        self.architecture = architecture
        self.codename = codename

        if ppas is None:
            ppas = []

        if exclusions is None:
            exclusions = []

        self._exclusions = exclusions
        self.ppas = ppas

        self._determined_exclusions = None

    def update(self, field, value):
        self.__setattr__(field, value)

    def determine_exclusions(self):
        self._determined_exclusions = gather_exclusions(self._exclusions)

    @property
    def exclusions(self):
        if self._determined_exclusions is None:
            self.determine_exclusions()
        return self._determined_exclusions
