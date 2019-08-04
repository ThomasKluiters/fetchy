import os
import io
import hashlib
import tarfile
import shutil

from fetchy.utils import get_cache_dir
from tarfile import TarInfo, TarFile
import unix_ar as arfile

from pathlib import Path


class DpkgInstaller(object):
    def __init__(self, downloader):
        self.downloader = downloader
        self.build_essential = [
            "base-passwd",
            "base-files",
            "hostname",
            "passwd",
            "sysv-rc",
            "dpkg",
            "dash",
            "sed",
            "grep",
            "gawk",
            "bash",
            "coreutils",
            "libc-bin",
            "diffutils",
            "findutils",
            "sysvinit-utils",
            "libpam-runtime",
            "gzip",
        ]

    def _download_files(self):
        self.files = self.downloader.download_packages(self.build_essential)

    def _create_builder_hash(self):
        sha = hashlib.sha256()
        for deb_file in self.files:
            sha.update(deb_file.package.download_url().encode())
        return sha.hexdigest()[:32]

    def _builder_cache_file(self):
        print(get_cache_dir())
        builder_path = Path(get_cache_dir(), "builder")
        if not builder_path.exists():
            builder_path.mkdir()

        return Path(builder_path, self._create_builder_hash())

    def _is_cached(self):
        return self._builder_cache_file().exists()

    def _build_image_tar(self, target_path):
        with tarfile.open(target_path, "w:gz") as image_tar:
            for directory in [
                ["./", "var", "lib", "dpkg", "info"],
                ["./", "var", "log"],
            ]:
                info = TarInfo("./" + Path(*directory).as_posix())
                info.type = tarfile.DIRTYPE
                image_tar.addfile(info)

            for file in [["var", "log", "dpkg.log"]]:
                image_tar.addfile(TarInfo("./" + Path(*file).as_posix()))

            status_file = io.BytesIO()

            for deb_file in self.files:
                deb_file.unpack_into_tar(image_tar, status_file)

            status_info = TarInfo(
                "./" + Path("var", "lib", "dpkg", "status").as_posix()
            )
            status_info.size = status_file.getbuffer().nbytes
            status_file.seek(0)

            image_tar.addfile(status_info, status_file)

            status_file.close()

    def _cache_tar(self, target_path):
        shutil.copyfile(target_path, self._builder_cache_file())

    def create_image_tar(self, target_path):
        self._download_files()
        if self._is_cached():
            shutil.copyfile(self._builder_cache_file(), target_path)
        else:
            print(
                "This is the first time using this environment.. building builder image.."
            )
            self._build_image_tar(target_path)
            self._cache_tar(target_path)


class DebianFile(object):
    def __init__(self, package, deb_file):
        self.package = package
        self.deb_file = deb_file

    def extract_from_file(self, name):
        package_file = arfile.open(self.deb_file)
        for info in package_file.infolist():
            if info.name.decode().startswith(name):
                return package_file.open(info.name.decode())
        package_file.close()
        return None

    def _append_to_status(self, status_file):
        status = "install ok unpacked"
        if self.package.name == "dash":
            status = "install ok installed"
        data = [
            f"Package: {self.package.name}",
            f"Status: {status}",
            f"Architecture: {self.package.arch}",
            f"Version: {self.package.version}",
            f"Provides: {', '.join(self.package.provides)}",
            f"Maintainer: a",
            f"Description: x",
        ]
        if self.package.dependencies:
            data.append(f"Depends: {', '.join(map(str, self.package.dependencies))}")
        if self.package.pre_dependencies:
            data.append(
                f"Pre-Depends: {', '.join(map(str, self.package.pre_dependencies))}"
            )
        status_file.write(str.encode("\n".join(data) + "\n\n"))

    def _unpack_info_file(self, tar: TarFile, member: TarInfo, fileobj: io.BytesIO):
        directory = Path("var", "lib", "dpkg", "info").as_posix()
        name = member.name.lstrip("./")

        member.name = f"./{directory}/{self.package.name}.{name}"

        tar.addfile(member, fileobj)

    def _unpack_control_data(self, tar: TarFile, control_archive: TarFile):
        for member in (member for member in control_archive if member.isfile()):
            with control_archive.extractfile(member) as fileobj:
                self._unpack_info_file(tar, member, fileobj)

    def _unpack_data(self, tar: TarFile, data_archive: TarFile):
        with io.BytesIO(
            str.encode(
                "\n".join(
                    [
                        member.name.lstrip(".")
                        for member in data_archive
                        if member.name.lstrip(".")
                    ]
                )
                + "\n"
            )
        ) as fileobj:
            info = TarInfo("list")
            info.size = fileobj.getbuffer().nbytes
            self._unpack_info_file(tar, info, fileobj)

        names = tar.getnames()

        for member in (member for member in data_archive if member.name not in names):
            if member.islnk() or member.issym() or member.isdir():
                tar.addfile(member)
            else:
                with data_archive.extractfile(member) as fileobj:
                    tar.addfile(member, fileobj)

    def unpack_into_tar(self, tar, status_file):
        debian_file_archive = arfile.open(self.deb_file)
        for info in debian_file_archive.infolist():
            with debian_file_archive.open(info.name.decode()) as content_archive:
                if info.name.decode().startswith("control"):
                    with tarfile.open(fileobj=content_archive) as control_archive:
                        self._unpack_control_data(tar, control_archive)
                if info.name.decode().startswith("data"):
                    with tarfile.open(fileobj=content_archive) as data_archive:
                        self._unpack_data(tar, data_archive)
        self._append_to_status(status_file)
        debian_file_archive.close()
