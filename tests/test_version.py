import pytest

from fetchy import Version, version_from_string


@pytest.mark.parametrize("input,epoch,upstream,debian", [
    ("42:1.0.0-alpha-3.2~", 42, "1.0.0-alpha", "3.2~"),
    ("42:1.0.0-alpha-3.2", 42, "1.0.0-alpha", "3.2"),
    ("42:1.0.0-3.2", 42, "1.0.0", "3.2"),
    ("42:1.0+2-3.2", 42, "1.0+2", "3.2"),
    ("1", 0, "1", "0")
])
def test_version_from_string(input, epoch, upstream, debian):
    result = version_from_string(input)

    assert result.upstream_version == upstream
    assert result.debian_revision == debian
    assert result.epoch == epoch

@pytest.mark.parametrize("input, expected", [
    (Version("1.0.0-alpha", "3.2~", 42), "42:1.0.0-alpha-3.2~"),
    (Version("1.0.0-alpha", "3.2", 42), "42:1.0.0-alpha-3.2"),
    (Version("1.0.0", "3.2", 42), "42:1.0.0-3.2"),
    (Version("1.0+2", "3.2", 42), "42:1.0+2-3.2")
])
def test_version_to_str(input, expected):
    assert str(input) == expected