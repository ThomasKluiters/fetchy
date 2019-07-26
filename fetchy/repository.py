class Repository(object):
    def __init__(self, packages_file, mirror, pkgs=None):
        """
        A Repository object stores and manages packages
        this way, we can use multiple package indices at once.
        """
        if pkgs is None:
            pkgs = {}
        self.packages_file = packages_file
        self.mirror = mirror
        self.pkgs = pkgs

    def add(self, pkg):
        """
        Add a single package to this Repository, if it already
        exists, then overwrite it.
        """
        self.pkgs[pkg.name] = pkg

    def update(self, pkgs):
        """
        Update this repository with dictionary of packages
        if this repository has already been populated with
        packages, then merge this repository with the packages.
        """
        if pkgs:
            return self.merge(Repository(self.packages_file, self.mirror, pkgs))
        self.pkgs = pkgs
        return self

    def merge(self, other):
        """
        Merge this repository with another repository, for now
        let's overwrite the packages in this repository with
        the packages in the other repository if they alreadu exist.
        """
        if not other.is_empty():
            for pkg in other.pkgs.values():
                self.add(pkg)
        return self

    def is_empty(self):
        """
        Return true if this repository has no packages.
        """
        return not bool(self.pkgs)

    def __getitem__(self, key):
        return self.pkgs.get(key, None)

    def __contains__(self, key):
        return key in self.pkgs
