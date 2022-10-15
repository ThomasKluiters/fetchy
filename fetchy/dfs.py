import os
import json
import tarfile
import docker
import shutil
import logging

from tarfile import TarInfo
from pathlib import Path
from tqdm import tqdm
from elftools.elf.elffile import ELFFile
from elftools.elf.dynamic import DynamicSection

from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


class DockerFileSystem(object):
    def __init__(self, from_image, image, client: docker.DockerClient):
        self.from_image = from_image
        self.loaded_layers = {}
        self.image = image
        self.client = client

    def _extract_image_in(self, directory):
        image = self.client.api.get_image(self.from_image)

        tar_file = os.path.join(directory, "image.tar")

        with open(tar_file, "wb") as tar:
            for chunk in image:
                tar.write(chunk)
        image.close()

        with tarfile.open(tar_file) as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, directory)

    def _extract_layers(self, directory):
        with open(os.path.join(directory, "manifest.json")) as manifest:
            self.layers = list(
                map(lambda x: x.split("/")[0], json.loads(manifest.read())[0]["Layers"])
            )

    def _find_file(self, directory, path, image_tar):
        for layer in reversed(self.layers):
            other_layer = self._get_layer(directory, layer)
            if path in other_layer.getnames():
                member = other_layer.getmember(path)
                image_tar.addfile(member, other_layer.extractfile(member))
                return

    def _find_library(self, directory, library, image_tar):
        for layer in reversed(self.layers):
            other_layer = self._get_layer(directory, layer)
            for file in [
                file for file in other_layer.getnames() if Path(file).name == library
            ]:
                member = other_layer.getmember(file)
                if member.isfile():
                    image_tar.addfile(member, other_layer.extractfile(member))
                    return

    def _remove_docker_files(self, directory, layer):
        layer_directory = os.path.join(directory, layer)

        for file_to_remove in ["layer.tar", "VERSION", "json"]:
            path = os.path.join(layer_directory, file_to_remove)
            if os.path.isfile(path):
                os.remove(path)

    def _remove_doc_files(self, directory, layer):
        with tqdm(total=5, desc="Removing documentation files...") as t:
            layer_directory = os.path.join(directory, layer)

            for directry_to_remove in [
                ["usr", "share", "doc"],
                ["usr", "share", "locale"],
                ["usr", "share", "man"],
                ["var", "lib", "dpkg"],
                ["var", "cache"],
            ]:
                path = os.path.join(*([layer_directory] + directry_to_remove))
                if os.path.isdir(path):
                    shutil.rmtree(path)
                t.update(1)

    def _check_binary(self, directory, layer_tar, image_tar, fileobj):
        fileobj.seek(0)
        if fileobj.read(4) != b"\x7fELF":
            fileobj.seek(0)
            return

        fileobj.seek(0)
        elf = ELFFile(fileobj)
        for section in [
            section
            for section in elf.iter_sections()
            if isinstance(section, DynamicSection)
        ]:
            for library in [
                tag.needed for tag in section.iter_tags() if hasattr(tag, "needed")
            ]:
                if not [
                    file
                    for file in (layer_tar.getnames() + image_tar.getnames())
                    if Path(file).name == library
                ]:
                    self._find_library(directory, library, image_tar)
        fileobj.seek(0)

    def _is_doc(self, path):
        for document_path in ["usr/share/doc", "usr/share/man", "usr/share/locale"]:
            if path.startswith(document_path):
                return True
        return False

    def _load_layer(self, directory, sha):
        self.loaded_layers[sha] = tarfile.open(os.path.join(directory, sha, "layer.tar"))

    def _get_layer(self, directory, sha):
        if sha not in self.loaded_layers:
            self._load_layer(directory, sha)

        return self.loaded_layers[sha]

    def _materialize_layers(self, directory, idx):
        for layer in reversed(self.layers[-idx:]):
            self._load_layer(directory, layer)

        count = sum([len(layer.getnames()) for layer in self.loaded_layers.values()])
        
        with tqdm(total=count, desc="Slimming down image") as t:
            with tarfile.open(
                os.path.join(directory, "image.tar"), "w:gz"
            ) as image_tar:
                for layer in reversed(self.layers[-idx:]):
                    with tarfile.open(
                        os.path.join(directory, layer, "layer.tar")
                    ) as layer_tar:
                        for member in layer_tar:
                            if self._is_doc(member.name) or member.name in image_tar.getnames():
                                continue
                            if member.islnk() or member.issym():
                                if member.linkname.startswith(
                                    "usr"
                                ) or member.linkname.startswith("bin"):
                                    name = member.linkname
                                else:
                                    name = Path(
                                        Path(member.name).parent, member.linkname
                                    )
                                target = os.path.normpath(name).lstrip("/")
                                if target not in (
                                    layer_tar.getnames() + image_tar.getnames()
                                ):
                                    self._find_file(directory, target, image_tar)
                                image_tar.addfile(member)
                            elif member.isfile():
                                fileobj = layer_tar.extractfile(member)
                                self._check_binary(
                                    directory, layer_tar, image_tar, fileobj
                                )
                                image_tar.addfile(member, fileobj)
                            else:
                                image_tar.addfile(member)
                            t.update(1)
                for base_dir in [
                    "tmp",
                    "var",
                    "sys",
                    "proc",
                    "run"
                ]:
                    if base_dir not in image_tar.getnames():
                        info = TarInfo(base_dir)
                        info.type = tarfile.DIRTYPE
                        image_tar.addfile(info)

        self.client.api.import_image(
            os.path.join(directory, "image.tar"), repository=self.image
        )

        for layer in self.loaded_layers.values():
            layer.close()

    def build_minimal_image(self):
        with TemporaryDirectory() as tmp:
            self._extract_image_in(tmp)
            self._extract_layers(tmp)
            self._materialize_layers(tmp, 1)
