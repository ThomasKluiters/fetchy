from fetchy import version_from_string


def relationship_from_string(string):
    """Function for parsing a single relationship

    This function will parse a single relationship
    into a DependencyRelationship object.

    Relationships are specified as following:
    (<relationship> <version>)
    """
    relationship, version = string.lstrip("( ").rstrip(" )").split(" ")
    return DependencyRelationship(relationship, version_from_string(version))


def dependency_from_string(kind, string):
    """Function for parsing a single dependency

    This function will parse a single dependency
    into a Dependency object.
    """
    string = string.strip()

    if "|" in string:
        dependencies = [
            dependency_from_string(kind, part) for part in string.split("|")
        ]
        return EitherDependency(kind, dependencies)

    (name, version, condition) = (None, None, None)

    version_idx_start = string.find("(")
    if version_idx_start != -1:
        version_idx_end = string.find(")")
        version_string = string[version_idx_start + 1 : version_idx_end]
        version = relationship_from_string(version_string)

    condition_idx_start = string.find("[")
    if condition_idx_start != -1:
        condition_idx_end = string.find("]")
        condition_string = string[condition_idx_start + 1 : condition_idx_end]
        condition = condition_string

    if (condition_idx_start != -1) and (version_idx_start != -1):
        name_idx_end = min(version_idx_start, condition_idx_start)
    elif condition_idx_start != -1:
        name_idx_end = condition_idx_start
    elif version_idx_start != -1:
        name_idx_end = version_idx_start
    else:
        name_idx_end = len(string)

    name = string[0:name_idx_end].strip()

    return SimpleDependency(kind, name, version, condition)


def dependencies_from_string(kind, string):
    """Function for parsing multiple dependencies

    This function will parse multiple dependencies
    in the form of a string, where each dependency
    is seperate by a comma.
    """
    if string is None:
        return []

    return [
        dependency_from_string(kind, dependency) for dependency in string.split(",")
    ]


class DependencyRelationship(object):
    def __init__(self, relationship, version):
        """A Relationship Object

        A relationship is a combination of specifier
        and a Version Object.

        Possible specifiers are:
        - `<<`, strictly earlier
        - `<=`, earlier or equal
        - `=`,  equal
        - `>=`, later or equal
        - `>>`, strictly later
        """
        self.relationship = relationship
        self.version = version


class Dependency(object):
    def __init__(self, kind):
        """A Dependency Object

        A dependency can either be a pre-dependency (`PreDepends`)
        or a 'normal' (`Depends`) dependency.

        A Dependency object is a combination
        of (possibly) multiple packages that
        should ultimately resolve to a single
        dependency.

        Cases where multiple dependencies are
        possible is when a dependency is constructed
        through the or (`|`) operator.
        """
        self.kind = kind

    def resolve(self):
        """Resolve Dependency

        This function will attempt to resolve
        a (possible) combination of multiple packages
        into a single package.
        """
        raise NotImplementedError(
            "The base dependency class does not resolve to anything!"
        )


class SimpleDependency(Dependency):
    def __init__(self, kind, name, relationship, condition):
        """
        A Simple Depency Object is a combination of a name and optionally
        a version specifier.

        Only the name of a Dependency is neccesary. If no version specifier
        is given then the latest package is used as a dependency.

        A version specifier may be supplied to give a constraint on which
        package may be a suitable dependency.

        Lastly, a dependency may have an optional condition under which
        it should be (or should not) be installed.

        Parameters
        ----------
        kind : string representing if this dependency is either a
            `Pre-Dependency` or `Dependency`.
        
        name : string representing the name of this dependency.

        rerlationship : the version specifier for this dependency must be
            an instance of :DependencyRelationship:.

        condition : a boolean condition under which this dependency
            must or must not be used.
        """
        super().__init__(kind)
        self.name = name
        self.relationship = relationship
        self.condition = condition

    def resolve(self):
        return [self.name]


class EitherDependency(Dependency):
    def __init__(self, kind, dependencies):
        """
        An EitherDependency contains a sequence of multiple dependencies.

        Each dependency can be used to 

        Parameters
        ----------
        kind : string representing if this dependency is either a
            `Pre-Dependency` or `Dependency`.
        
        dependencies : a list of Dependency objects which can be used
            to satisfy the dependency.
        """
        super().__init__(kind)
        self.dependencies = dependencies

    def resolve(self):
        return [dependency.name for dependency in self.dependencies]
