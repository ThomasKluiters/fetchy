import fetchy as fty

import tempfile


class Fetchy(object):
    def __init__(self, config=None):
        if config is None:
            config = fty.config_from_env()
        self.config = config
        self._repository = None

    def build_repository(self):
        repository = fty.get_packages_control_file(
            self.config.distribution,
            self.config.version,
            self.config.architecture,
            self.config.mirror,
        )

        fty.Parser(repository).parse()

        for ppa in self.config.ppas:
            ppa_repository = fty.get_packages_control_file(
                self.config.distribution,
                self.config.version,
                self.config.architecture,
                ppa=ppa,
            )

            fty.Parser(ppa_repository).parse()
            repository.merge(ppa_repository)
        return repository

    @property
    def repository(self):
        if self._repository is None:
            self._repository = self.build_repository()
        return self._repository

    def download_packages(self, out_dir, packages_to_download):
        return fty.Downloader(self.repository, out_dir=out_dir).download_package(
            packages_to_download, self.config.exclusions
        )

    def extract_packages(self, extract_dir, packages_to_extract):
        temp_download_dir = tempfile.mkdtemp()

        downloaded_packages = self.download_packages(
            temp_download_dir, packages_to_extract
        )

        fty.Extractor(extract_dir).extract_all(downloaded_packages)

    def dockerize_packages(self, tag, packages_to_dockerize):
        temp_extract_dir = tempfile.mkdtemp()
        self.extract_packages(temp_extract_dir, packages_to_dockerize)

        import os

        os.listdir(temp_extract_dir)

        fty.Dockerizer(tag, temp_extract_dir).build()