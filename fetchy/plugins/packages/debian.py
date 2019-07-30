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
            "dpkg",
            "dash",
            "sed",
            "grep",
            "gawk",
            "coreutils",
            "libc-bin",
            "diffutils",
            "findutils",
            "sysvinit-utils",
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

    def cleanup(self, context, excludes, includes):
        remove_order = [
            "install-info",
            "libc-bin",
            "diffutils",
            "debianutils",
            "sysvinit-utils",
            "sed",
            "libgmp10",
            "libmpfr6",
            "grep",
            "readline-common",
            "libsigsegv2",
            "tar",
            "gzip",
            "libcre6",
            "dpkg dash coreutils",
        ]

        remove_order_filtered = [
            package for package in excludes if package not in remove_order
        ] + [package for package in remove_order if package not in includes]

        remove_script = "\n".join([] + list(
            map(lambda x: f"dpkg --purge --force-all {x}", remove_order_filtered)
        )) + "\n"
        return remove_script


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
            data = [
                f"Package: {self.package.name}",
                f"Status: install ok unpacked",
                f"Architecture: {self.package.arch}",
                f"Version: {self.package.version}",
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

    @property
    def data(self):
        return self.extract_from_file("data")

    @property
    def files(self):
        tar_file = tarfile.open(fileobj=self.data)
        return [info.name for info in tar_file.getmembers() if info.isfile()]

    @property
    def control(self):
        scripts = {}
        with tarfile.open(fileobj=self.extract_from_file("control")) as tar_file:
            for member in tar_file.getmembers():
                if member.isfile():
                    scripts[member.name.lstrip("./")] = tar_file.extractfile(
                        member
                    ).read()
        return scripts

    def extract(self, context):
        with tarfile.open(fileobj=self.data) as tar_file:
            tar_file.extractall(context)

    def create_install_script(self, context):
        scripts = []
        if "preinst" in self.control:
            install_script_file = Path(context, self.package.name, "preinstall.sh")
            with open(install_script_file, "wb") as install_script:
                install_script.write(self.control["preinst"])
            scripts.append(f"/scripts/{self.package.name}/preinstall.sh")
        if "postinst" in self.control:
            install_script_file = Path(context, self.package.name, "install.sh")
            with open(install_script_file, "wb") as install_script:
                install_script.write(self.control["postinst"])
            scripts.append(f"/scripts/{self.package.name}/install.sh configure")
        return scripts

    def create_remove_scripts(self, context):
        remove_file_script = Path(context, self.package.name, "remove_files.sh")

        scripts = []
        with open(remove_file_script, "w") as remove_script:
            remove_script.write("#!/bin/sh\n")
            remove_script.write("\n".join([f"rm {file}" for file in self.files]))
            scripts.append(f"/scripts/{self.package.name}/remove_files.sh")
        if "postrm" in self.control:
            post_remove_file = Path(context, self.package.name, "post_remove.sh")
            with open(post_remove_file, "wb") as post_remove_script:
                post_remove_script.write(self.control["postrm"])
            scripts.append(f"/scripts/{self.package.name}/post_remove.sh")
        return scripts
