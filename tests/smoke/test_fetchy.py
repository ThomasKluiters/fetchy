import pytest
import tempfile

from fetchy import Fetchy, FetchyConfig


def get_fetchy():
    return Fetchy(FetchyConfig("ubuntu", "bionic", "amd64"))


def get_fetchy_with_ppa(ppas):
    return Fetchy(FetchyConfig("ubuntu", "bionic", "amd64", ppas=ppas))


@pytest.mark.smoke
def test_extract_one_package(tmpdir):
    get_fetchy().extract_packages(tmpdir, ["gcc-8-base"])


@pytest.mark.smoke
def test_extract_multiple_packages(tmpdir):
    get_fetchy().extract_packages(tmpdir, ["libgcc1", "gcc-8-base"])


@pytest.mark.smoke
def test_extract_package_with_ppa(tmpdir):
    get_fetchy_with_ppa(["deadsnakes"]).extract_packages(tmpdir, ["python3.8"])
