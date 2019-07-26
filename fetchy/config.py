from fetchy import (
    get_architecture,
    get_distribution,
    get_distribution_version,
    get_mirror,
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
        version=None,
        architecture=None,
        mirror=None,
        ppas=None,
        exclusions=None,
    ):
        self.distribution = distribution
        self.architecture = architecture
        self.version = version
        self._mirror = mirror

        if ppas is None:
            ppas = []

        if exclusions is None:
            exclusions = []

        self._exclusions = exclusions
        self.ppas = ppas

        self._determined_exclusions = None

    def update(self, field, value):
        self.__setattr__(field, value)

    def determine_mirror(self):
        self._mirror = get_mirror(self.distribution)

    def determine_exclusions(self):
        self._determined_exclusions = gather_exclusions(self._exclusions)

    @property
    def exclusions(self):
        if self._determined_exclusions is None:
            self.determine_exclusions()
        return self._determined_exclusions

    @property
    def mirror(self):
        if self._mirror is None:
            self.determine_mirror()
        return self._mirror
