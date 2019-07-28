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
            ]
        self.source = source
        self.fields = fields

    def parse(self):
        """
        Consume the source package indices and add the packages to
        a repository file.
        """
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

        return repository
