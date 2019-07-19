class Parser(object):
    def __init__(self, packages_file, fields=None):
        """The Control File Parser

        This class is responsible for parsing
        control files.

        Control files contain the list of dependencies
        one would require to find the desired packages.
        """
        if fields is None:
            fields = ["Package", "Version", "Depends", "Pre-Depends", "Filename"]
        self.packages_file = packages_file
        self.fields = fields

    def parse_packages_raw(self, fp):
        pkg = {}
        for line in fp:
            for field in self.fields:
                if line.startswith(field):
                    pkg[field] = line.rstrip()[(len(field) + 2) :]

            # New packages are introduced with whitespaces
            if line.startswith("\r\n") or line.startswith("\n"):
                if pkg:
                    yield pkg
                    pkg = {}

    def parse(self):
        pkgs = {}
        with open(self.packages_file, "r") as fp:
            for pkg in self.parse_packages_raw(fp):
                pkgs[pkg["Package"]] = pkg
