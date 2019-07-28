import os
import tempfile

from fetchy.plugins import BasePlugin

from .source import DefaultUbuntuSource, DefaultDebianSource, DefaultPPASource
from .repository import Repository
from .downloader import Downloader
from .extractor import Extractor
from .parser import Parser

from logging import Logger

logger = Logger(__name__)


class PackagesPlugin(BasePlugin):
    def __init__(self, data):
        super(PackagesPlugin, self).__init__(
            "Packages plugin",
            "packages",
            "The packages plugin manages dependencies for distributions.",
        )
        self.exclude = data.get("exclude", [])
        self.ppa = data.get("ppa", [])
        self.fetch = data["fetch"]

    def validate(self):
        if not self.fetch:
            logger.error("Packages module expects field `fetch` to be present.")
            return False
        if not isinstance(self.fetch, list):
            logger.error("Packages module expects field `fetch` to be a list.")
            return False
        return True

    def _build_repository(self):
        sources = []

        if self.blueprint.distribution == "ubuntu":
            sources.append(
                DefaultUbuntuSource(
                    self.blueprint.codename, self.blueprint.architecture
                )
            )
        elif self.blueprint.distribution == "debian":
            sources.append(
                DefaultDebianSource(
                    self.blueprint.codename, self.blueprint.architecture
                )
            )
        for ppa in self.ppa:
            sources.append(
                DefaultPPASource(
                    ppa, self.blueprint.codename, self.blueprint.architecture
                )
            )

        repository = Repository()
        for source in sources:
            repository.merge(Parser(source).parse())
        return repository

    def _gather_exclusions(self):
        """
        Gathers a list of dependencies that should be excluded.

        Exclusion values ending with a .txt extension will be
        parsed as files and will read these files line by line.
        """
        dependencies_to_exclude = []

        for exclusion in self.exclude:
            if exclusion.endswith(".txt"):
                with open(exclusion, "r") as exclusion_file:
                    for exclusion_line in exclusion_file:
                        dependencies_to_exclude.append(exclusion_line.strip())

            else:
                dependencies_to_exclude.append(exclusion)

        return dependencies_to_exclude

    def _download_and_extract(self, context):
        repository = self._build_repository()

        packages_directory = self._dir_in_context(context)

        downloader = Downloader(repository, tempfile.mkdtemp())
        extractor = Extractor(packages_directory)

        extractor.extract_all(
            downloader.download_packages(self.fetch, self._gather_exclusions())
        )

        context.dockerfile.copy(self._dir_name(), "/")

    def build(self, context):
        self._download_and_extract(context)
