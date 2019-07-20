from fetchy import version_from_string, dependencies_from_string


def package_from_dict(dictionary):
    if "Package" not in dictionary:
        raise RuntimeError("Mandatory package field is not present!")
    if "Version" not in dictionary:
        raise RuntimeError("Mandatory version field is not present!")
    if "Architecture" not in dictionary:
        raise RuntimeError("Mandatory architecture field is not present!")

    return Package(
        dictionary["Package"],
        version_from_string(dictionary["Version"]),
        dictionary["Architecture"],
        dependencies_from_string("Depends", dictionary.get("Depends")),
        dependencies_from_string("Pre-Depends", dictionary.get("Pre-Depends")),
        dictionary.get("Filename"),
    )


def unify(left, right):
    if left.name == right.name:
        if left.version.is_greater(right.version):
            return left
        else:
            return right


class Package(object):
    def __init__(
        self, name, version, arch, dependencies=[], pre_dependencies=[], filename=None
    ):
        """A Package Object
        
        A Package object is a slimmed down version
        of a debian package.

        We only care about a subset of information
        of the package for our purpose:
        - Name
        - Version
        - Architecture
        - Dependencies
        - Pre-Dependencies
        - Filename
        """
        self.name = name
        self.version = version
        self.arch = arch
        self.dependencies = dependencies
        self.pre_dependencies = pre_dependencies
        self.filename = filename

    def file_name(self):
        if self.file_name is None:
            return f"{self.name}-{self.version}"
