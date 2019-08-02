import os
import json
import tarfile
import docker
import shutil
import logging

from pathlib import Path
from tqdm import tqdm
from elftools.elf.elffile import ELFFile
from elftools.elf.dynamic import DynamicSection

from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


class DockerFileSystem(object):
    def __init__(self, from_image, image, client: docker.DockerClient):
        self.from_image = from_image
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
            tar.extractall(directory)

    def _extract_layers(self, directory):
        with open(os.path.join(directory, "manifest.json")) as manifest:
            self.layers = list(
                map(lambda x: x.split("/")[0], json.loads(manifest.read())[0]["Layers"])
            )

        with tqdm(total=len(self.layers), desc="Extracting layers...") as t:
            for layer in self.layers:
                with tarfile.open(
                    os.path.join(directory, layer, "layer.tar")
                ) as layer_tar:
                    layer_tar.extractall(os.path.join(directory, layer))
                    t.update(1)

    def _find_file(self, directory, path):
        for layer in reversed(self.layers):
            path_in_layer = os.path.join(directory, layer, path)
            if os.path.isfile(path_in_layer):
                return (layer, path_in_layer)
        return (None, None)

    def _find_library(self, directory, library):
        for layer in reversed(self.layers):
            path_in_layer = os.path.join(directory, layer)
            for root, _, files in os.walk(path_in_layer):
                for file in files:
                    if library in file:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, path_in_layer)
                        return (layer, rel_path, full_path)
        return (None, None, None)

    def _remove_docker_files(self, directory, layer):
        layer_directory = os.path.join(directory, layer)

        for file_to_remove in ["layer.tar", "VERSION", "json"]:
            path = os.path.join(layer_directory, "layer.tar")
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

    def _check_binary(self, path, layer, directory, tar):
        with open(path, "rb") as binary_file:
            if binary_file.read(4) != b"\x7fELF":
                return

        with open(path, "rb") as binary_file:
            elf = ELFFile(binary_file)
            for section in elf.iter_sections():
                if isinstance(section, DynamicSection):
                    for tag in section.iter_tags():
                        if hasattr(tag, "needed"):
                            (
                                resolved_layer,
                                resolved_name,
                                resolved_library,
                            ) = self._find_library(directory, tag.needed)
                            if (
                                resolved_layer != layer
                                and resolved_name not in tar.getnames()
                            ):
                                tar.add(resolved_library, arcname=resolved_name)

    def _materialize_last_layer(self, directory):
        layer = self.layers[-1]

        self._remove_doc_files(directory, layer)
        self._remove_docker_files(directory, layer)

        layer_directory = os.path.join(directory, layer)

        with tarfile.open(os.path.join("./", "image.tar"), "w:gz") as tar:
            with tqdm(
                total=sum([len(files) for (_, _, files) in os.walk(layer_directory)]),
                desc="Verifying image...",
            ) as t:
                for root, dirs, files in os.walk(layer_directory):
                    for _dir in dirs:
                        tar_dir = tarfile.TarInfo(
                            os.path.relpath(os.path.join(root, _dir), layer_directory)
                        )
                        tar_dir.type = tarfile.DIRTYPE
                        tar_dir.mode = 0o777
                        tar.addfile(tar_dir)
                    for file in [
                        os.path.join(root, file) for file in files if ".wh." not in file
                    ]:
                        name = os.path.relpath(file, layer_directory)
                        if os.path.islink(file):

                            if os.readlink(file).startswith(
                                "/"
                            ):  # symlink was picked up by our system..
                                if layer_directory in os.readlink(file):
                                    missing = os.path.relpath(
                                        os.readlink(file), layer_directory
                                    )
                                else:
                                    missing = os.readlink(file).lstrip("/")
                            else:
                                if os.path.basename(os.readlink(file)) == os.readlink(
                                    file
                                ):
                                    missing = os.path.relpath(
                                        os.path.join(root, os.readlink(file)),
                                        layer_directory,
                                    )
                                else:
                                    missing = os.path.relpath(
                                        os.path.join(
                                            os.path.dirname(file), os.readlink(file)
                                        ),
                                        layer_directory,
                                    )

                            (resolved_layer, resolved) = self._find_file(
                                directory, missing
                            )

                            if not resolved:
                                logger.warn(
                                    f"Missing {missing}, you may want to include this file."
                                )
                            elif resolved_layer != layer:
                                target = os.path.join(layer_directory, missing)

                                if not os.path.isfile(target):
                                    if (
                                        Path(target).resolve()
                                        != Path(resolved).resolve()
                                    ):
                                        shutil.copyfile(resolved, target)

                                    tar.add(resolved, arcname=missing)
                        if name not in tar.getnames():
                            tar.add(file, arcname=name)
                        t.update(1)

            for binary in os.listdir(os.path.join(layer_directory, "usr", "bin")):
                path = os.path.join(layer_directory, "usr", "bin", binary)
                if os.path.isfile(path):
                    self._check_binary(path, layer, directory, tar)

        self.client.api.import_image(
            os.path.join("./", "image.tar"), repository=self.image
        )

    def build_minimal_image(self):
        with TemporaryDirectory() as tmp:
            self._extract_image_in(tmp)
            self._extract_layers(tmp)
            self._materialize_last_layer(tmp)
