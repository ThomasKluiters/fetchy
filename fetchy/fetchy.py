import fetchy as fty

import tempfile


class Fetchy(object):
    def __init__(self, config=None):
        if config is None:
            config = fty.config_from_env()
        self.config = config
        self._repository = None

    def build_repository(self):
        sources = []
        if self.config.distribution == "ubuntu":
            sources.append(
                fty.DefaultUbuntuSource(self.config.codename, self.config.architecture)
            )
        elif self.config.distribution == "debian":
            sources.append(
                fty.DefaultDebianSource(self.config.codename, self.config.architecture)
            )
        for ppa in self.config.ppas:
            sources.append(
                fty.DefaultPPASource(
                    ppa, self.config.codename, self.config.architecture
                )
            )

        repository = fty.Repository()
        for source in sources:
            repository.merge(fty.Parser(source).parse())
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

        return fty.Extractor(extract_dir).extract_all(downloaded_packages)

    def dockerize_packages(self, tag, packages_to_dockerize):
        temp_extract_dir = tempfile.mkdtemp()
        binaries = self.extract_packages(temp_extract_dir, packages_to_dockerize)

        return fty.Dockerizer(tag, temp_extract_dir).build(binaries)
