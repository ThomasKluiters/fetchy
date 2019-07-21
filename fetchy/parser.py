from fetchy import Repository, package_from_dict


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
        self.repository = Repository({})

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
        if not self.repository.is_empty():
            return self.repository

        with open(self.packages_file, "r") as fp:
            pkg = {}
            for line in fp:
                # New packages are introduced with whitespaces
                if line.startswith("\r\n") or line.startswith("\n"):
                    if pkg:
                        self.repository.add(package_from_dict(pkg))
                        pkg = {}

                for field in self.fields:
                    if line.startswith(field):
                        pkg[field] = line.rstrip()[(len(field) + 2) :]
                        break
                        
        return self.repository
