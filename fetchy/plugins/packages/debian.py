import os
import tarfile
import unix_ar as arfile

from pathlib import Path


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
        if "postinst" in self.control:
            install_script_file = Path(context, self.package.name, "install.sh")
            with open(install_script_file, "wb") as install_script:
                install_script.write(self.control["postinst"])
            scripts.append(f"/scripts/{self.package.name}/install.sh")
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
