from fetchy import package_from_dict


class Parser(object):
    def __init__(self, packages_file, fields=None):
        """The Control File Parser

        This class is responsible for parsing
        control files.

        Control files contain the list of dependencies
        one would require to find the desired packages.
        """
        if fields is None:
            fields = [
                "Package",
                "Version",
                "Depends",
                "Pre-Depends",
                "Filename",
                "Architecture",
            ]
        self.packages_file = packages_file
        self.fields = fields

    def _parse_packages_raw(self, fp):
        """Function that yields packages as dictionaries

        This function will fully consume the
        file and yield each package as a dictionary.

        The dictionary will be populated with fields
        that are supplied to this Parsers' Constructor.

        Note that this function will work as a generator,
        if you want to fetch all packages at once, use
        `list(_parse_packages_raw)`.
        """
        pkg = {}
        for line in fp:
            # New packages are introduced with whitespaces
            if line.startswith("\r\n") or line.startswith("\n"):
                if pkg:
                    yield pkg
                    pkg = {}

            for field in self.fields:
                if line.startswith(field):
                    pkg[field] = line.rstrip()[(len(field) + 2) :]
                    break

    def parse(self):
        """Function that parses all packages

        This function will parse all packages into
        a `Package` object. Returning a dictionary
        where each package is stored with its' name
        as a key.        

        Note that each `Package` object will only
        be populated with the fields that are
        supplied to this Parsers' Constructor.
        """
        pkgs = {}
        with open(self.packages_file, "r") as fp:
            for pkg in self._parse_packages_raw(fp):
                pkgs[pkg["Package"]] = package_from_dict(pkg)
        return pkgs
