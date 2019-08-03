import os
import urllib
import gzip
import shutil
import hashlib

from .mirror import PersonalPackageArchiveMirror, UbuntuMirror, DebianMirror
from pathlib import Path
from tqdm import tqdm


class Source(object):
    def __init__(self):
        """
        A Source is a collection of package indices that Fetchy should consider
        when doing dependency resolution.
        """
        pass

    def collect_package_indices(self):
        raise NotImplementedError()

    def _download_files(self):
        if not os.path.exists(self._get_sources_dir()):
            os.makedirs(self._get_sources_dir())

        package_index_files = self.collect_package_indices()
        package_file_path = self._get_file_name()

        with tqdm(
            total=len(package_index_files), desc="Downloading archive indices"
        ) as t:
            with open(package_file_path, "wb") as package_file:
                for package_index_url in package_index_files:
                    (package_index_file, _) = urllib.request.urlretrieve(
                        package_index_url
                    )
                    with gzip.open(package_index_file) as package_index_data:
                        shutil.copyfileobj(package_index_data, package_file)
                        t.update(1)

    def _get_sources_dir(self):
        if "XDG_CACHE_HOME" in os.environ:
            return os.path.join(os.environ["XDG_CACHE_HOME"], "fetchy")
        return os.path.join(str(Path.home()), ".cache", "fetchy")

    def _create_hash(self):
        """
        Creates a hash based on the configuration of this Source.
        
        The hash should uniquely identify a source configuration,
        without having to store a massive string.
        """
        sha = hashlib.sha256()
        for index in self.collect_package_indices():
            sha.update(index.encode())
        return sha.hexdigest()[:32]

    def _get_file_name(self):
        return os.path.join(self._get_sources_dir(), str(self._create_hash()))

    def get_index_file(self):
        if not os.path.isfile(self._get_file_name()):
            self._download_files()
        return self._get_file_name()


class DebianBasedSource(Source):
    def __init__(self, mirror, codename, architecture, repositories, updates):
        """
        A Debian Based Source object that can be used to navigate debian based
        package archives.

        Parameters
        ----------
        mirror : the mirror to use to download the source packages
        codename : the codename of the version of the distribution to use
        architecture : the target architecture of the packages
        repositories : a list of repositories to consider, for example `universe` or
            `main` for ubuntu or `contrib` and `main` for debian.
        updates : a list of updates to consider, any of `updates`, `security`, `backported`
            or `proposed`.
        """
        self.mirror = mirror
        self.codename = codename
        self.architecture = architecture
        self.repositories = repositories
        self.updates = updates

    def collect_package_indices(self):
        """
        Collects a list of urls that point to package indices which must be
        downloaded to represent this Source object.
        """
        mirror_url = self.mirror.url()

        urls = []
        for repository in self.repositories:
            urls.append(
                f"{mirror_url}dists/{self.codename}/{repository}/binary-{self.architecture}/Packages.gz"
            )
            for update in self.updates:
                urls.append(
                    f"{mirror_url}dists/{self.codename}-{update}/{repository}/binary-{self.architecture}/Packages.gz"
                )
        return urls


class PersonalPackageArchiveSource(DebianBasedSource):
    def __init__(self, archive, codename, architecture):
        super(PersonalPackageArchiveSource, self).__init__(
            archive, codename, architecture, ["main"], []
        )


class DefaultDebianSource(DebianBasedSource):
    def __init__(self, codename, architecture):
        super(DefaultDebianSource, self).__init__(
            DebianMirror(), codename, architecture, ["main"], ["updates"]
        )


class DefaultUbuntuSource(DebianBasedSource):
    def __init__(self, codename, architecture):
        super(DefaultUbuntuSource, self).__init__(
            UbuntuMirror(),
            codename,
            architecture,
            ["main", "universe"],
            ["updates", "security"],
        )


class DefaultPPASource(PersonalPackageArchiveSource):
    def __init__(self, name_or_url, codename, architecture):
        super(DefaultPPASource, self).__init__(
            PersonalPackageArchiveMirror(name_or_url), codename, architecture
        )
