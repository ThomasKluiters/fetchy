class Repository(object):
    def __init__(self, pkgs={}):
        """
        A Repository object stores and manages packages
        this way, we can use multiple package indices at once.
        """
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
            return self.merge(Repository(pkgs))
        self.pkgs = pkgs
        return self
    
    def merge(self, other):
        """
        Merge this repository with another repository, for now
        let's overwrite the packages in this repository with
        the packages in the other repository if they alreadu exist.
        """
        if other.pkgs:
            for pkg in other.pkgs.values():
                self.add(pkg)
        return self

    def is_empty(self):
        """
        Return true if this repository has no packages.
        """
        return not bool(self.pkgs)

    def __getitem__(self, key):
        return self.pkgs[key]