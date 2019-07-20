import pytest

from fetchy import relationship_from_string, dependency_from_string


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
