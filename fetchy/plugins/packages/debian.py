import os
import io
import tarfile
import shutil
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

    def download(self):
        self.files = self.downloader.download_packages(self.build_essential)

    def install(self, context):
        os.makedirs(os.path.join(context, "var", "lib", "dpkg", "info"))
        os.makedirs(os.path.join(context, "var", "log"))

        Path(context, "var", "lib", "dpkg", "status").touch()
        Path(context, "var", "log", "dpkg.log").touch()

        self.download()
        for deb_file in self.files:
            deb_file.unpack(context)

        return [file.package.name for file in self.files]


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

    def _append_to_status(self, context):
        dpkg_status_file = os.path.join(context, "var", "lib", "dpkg", "status")
        with open(dpkg_status_file, "a") as status_file:
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
                data.append(
                    f"Depends: {', '.join(map(str, self.package.dependencies))}"
                )
            if self.package.pre_dependencies:
                data.append(
                    f"Pre-Depends: {', '.join(map(str, self.package.pre_dependencies))}"
                )
            status_file.write("\n".join(data) + "\n\n")

    def _unpack_info_file(self, context, name, file):
        dpkg_info_dir = os.path.join(context, "var", "lib", "dpkg", "info")
        dpkg_info_file = f"{self.package.name}.{name}"
        with open(os.path.join(dpkg_info_dir, dpkg_info_file), "wb") as info_file:
            shutil.copyfileobj(file, info_file)
        os.chmod(os.path.join(dpkg_info_dir, dpkg_info_file), 0o777)

    def _unpack_control_data(self, context, control_archive):
        for member in control_archive.getmembers():
            if member.isfile():
                with control_archive.extractfile(member) as control_file:
                    self._unpack_info_file(
                        context, member.name.lstrip("./"), control_file
                    )

    def _unpack_data(self, context, data_archive):
        files = [
            member.name.lstrip(".") + "\n"
            for member in data_archive.getmembers()
            if len(member.name.lstrip(".")) != 0
        ]

        self._unpack_info_file(context, "list", io.BytesIO(str.encode("".join(files))))
        data_archive.extractall(context)

    def unpack(self, context):
        debian_file_archive = arfile.open(self.deb_file)
        for info in debian_file_archive.infolist():
            with debian_file_archive.open(info.name.decode()) as content_archive:
                if info.name.decode().startswith("control"):
                    with tarfile.open(fileobj=content_archive) as control_archive:
                        self._unpack_control_data(context, control_archive)
                if info.name.decode().startswith("data"):
                    with tarfile.open(fileobj=content_archive) as data_archive:
                        self._unpack_data(context, data_archive)
        self._append_to_status(context)
