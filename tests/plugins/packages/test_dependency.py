import pytest

from fetchy.plugins.packages.dependency import relationship_from_string, dependency_from_string, EitherDependency


@pytest.mark.parametrize(
    "input,relationship,version",
    [
        ("(>= 2:12-alpha-3.2)", ">=", "12-alpha"),
        ("(     = 3   )", "=", "3"),
        ("(= 3)", "=", "3"),
    ],
)
def test_relationship(input, relationship, version):
    result = relationship_from_string(input)

    assert result.relationship == relationship
    assert result.version.upstream_version == version


@pytest.mark.parametrize(
    "input,name",
    [
        ("python3", "python3"),
        ("python3 (= 3)", "python3"),
        ("python3 [] (= 3)", "python3"),
    ],
)
def test_dependency_name(input, name):
    result = dependency_from_string("", input)

    assert result.name == name


@pytest.mark.parametrize(
    "input,names",
    [
        ("java | python3", ["java", "python3"]),
        ("java | python3 (= 3)", ["java", "python3"]),
        ("java | python3 [] (= 3)", ["java", "python3"]),
    ],
)
def test_dependency_either(input, names):
    result = dependency_from_string("", input)

    assert isinstance(result, EitherDependency)
    assert result.dependencies[0].name in names
    assert result.dependencies[1].name in names
