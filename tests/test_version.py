import pytest

from fetchy import version_from_string


@pytest.mark.parametrize("input,epoch,upstream,debian", [
    ("42:1.0.0-alpha-3.2~", 42, "1.0.0-alpha", "3.2~"),
    ("42:1.0.0-alpha-3.2", 42, "1.0.0-alpha", "3.2"),
    ("42:1.0.0-3.2", 42, "1.0.0", "3.2"),
    ("42:1.0+2-3.2", 42, "1.0+2", "3.2"),
    ("1", 0, "1", "0")
])
def test_just_upstream(input, epoch, upstream, debian):
    version = version_from_string(input)

    assert version.upstream_version == upstream
    assert version.debian_revision == debian
    assert version.epoch == epoch
