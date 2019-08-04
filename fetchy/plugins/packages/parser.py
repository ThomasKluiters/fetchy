import pickle

from pathlib import Path
from fetchy.utils import get_cache_dir

from .repository import Repository
from .package import package_from_dict


class Parser(object):
    def __init__(self, source, fields=None):
        """
        The Control File Parser will parse package archive
        index files into a Repository object.

        Control files contain the list of dependencies
        one would require to find the desired packages.

        Parameters
        ----------
        source : the source this parser will consume, an instance
            of a Source object
        """
        if fields is None:
            fields = [
                "Package",
                "Version",
                "Depends",
                "Pre-Depends",
                "Filename",
                "Architecture",
                "Installed-Size",
                "Provides",
            ]
        self.source = source
        self.fields = fields

    def _get_cache_path(self):
        return Path(get_cache_dir(), self.source._create_hash() + ".pkl")

    def _load_from_cache(self):
        if self._get_cache_path().exists():
            with open(self._get_cache_path(), "rb") as pkl_file:
                return pickle.load(pkl_file)

    def parse(self):
        """
        Consume the source package indices and add the packages to
        a repository file.
        """
        if self._get_cache_path().exists():
            return self._load_from_cache()

        repository = Repository()
        with open(self.source.get_index_file(), "r", encoding="utf-8") as fp:
            pkg = {}
            for line in fp:
                # New packages are introduced with whitespaces
                if line.startswith("\r\n") or line.startswith("\n"):
                    if pkg:
                        repository.add(package_from_dict(pkg, self.source.mirror.url()))
                        pkg = {}

                for field in self.fields:
                    if line.startswith(field):
                        pkg[field] = line.rstrip()[(len(field) + 2) :]
                        break

        if not self._get_cache_path().exists():
            with open(self._get_cache_path(), "wb") as pkl_file:
                pickle.dump(repository, pkl_file)

        return repository
