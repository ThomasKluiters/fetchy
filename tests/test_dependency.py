import pytest

from fetchy import relationship_from_string


@pytest.mark.parametrize("input,relationship,version", [
    ("(>= 2:12-alpha-3.2", ">=", "12-alpha"),
    ("(     = 3   )", "=", "3"),
    ("(= 3)", "=", "3")
])
def test_test_relationship(input, relationship, version):
    result = relationship_from_string(input)

    assert result.relationship == relationship
    assert result.version.upstream_version == version
