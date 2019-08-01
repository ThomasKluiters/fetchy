import os
import json
import tarfile
import docker
import shutil

from tempfile import TemporaryDirectory

class DockerFileSystem(object):
    def __init__(self, image, client : docker.DockerClient):
        self.image = image
        self.client = client

    def _extract_image_in(self, directory):
        image = self.client.api.get_image(self.image)

        tar_file = os.path.join(directory, "image.tar")

        with open(tar_file, 'wb') as tar:
            for chunk in image:
                tar.write(chunk)
        image.close()

        with tarfile.open(tar_file) as tar:
            tar.extractall(directory)
        

    def _extract_layers(self, directory):
        with open(os.path.join(directory, "manifest.json")) as manifest:
            self.layers = list(map(lambda x: x.split("/")[0], json.loads(manifest.read())[0]["Layers"]))

        for layer in self.layers:
            with tarfile.open(os.path.join(directory, layer, "layer.tar")) as layer_tar:
                layer_tar.extractall(os.path.join(directory, layer))

    def _find_file(self, directory, path):
        for layer in reversed(self.layers):
            path_in_layer = os.path.join(directory, layer, path)
            if os.path.isfile(path_in_layer):
                return path_in_layer
    
    def _remove_docker_files(self, directory, layer):
        layer_directory = os.path.join(directory, layer)

        if os.path.isfile(os.path.join(layer_directory, "layer.tar")):
            os.remove(os.path.join(layer_directory, "layer.tar"))

        if os.path.isfile(os.path.join(layer_directory, "VERSION")):
            os.remove(os.path.join(layer_directory, "VERSION"))

        if os.path.isfile(os.path.join(layer_directory, "json")):
            os.remove(os.path.join(layer_directory, "json"))

    def _remove_doc_files(self, directory, layer):
        layer_directory = os.path.join(directory, layer)

        if os.path.isdir(os.path.join(layer_directory, "usr", "share", "doc")):
            shutil.rmtree(os.path.join(layer_directory, "usr", "share", "doc"))

        if os.path.isdir(os.path.join(layer_directory, "usr", "share", "locale")):
            shutil.rmtree(os.path.join(layer_directory, "usr", "share", "locale"))

        if os.path.isdir(os.path.join(layer_directory, "usr", "share", "man")):
            shutil.rmtree(os.path.join(layer_directory, "usr", "share", "man"))

        if os.path.isdir(os.path.join(layer_directory, "var", "lib", "dpkg")):
            shutil.rmtree(os.path.join(layer_directory, "var", "lib", "dpkg"))

        if os.path.isdir(os.path.join(layer_directory, "var", "cache")):
            shutil.rmtree(os.path.join(layer_directory, "var", "cache"))

    def _materialize_last_layer(self, directory):
        layer = self.layers[-1]

        self._remove_doc_files(directory, layer)
        self._remove_docker_files(directory, layer)
        
        layer_directory = os.path.join(directory, layer)

        with tarfile.open(os.path.join(directory, "image.tar"), "w:gz") as tar:
            for root, dirs, files in os.walk(layer_directory):
                for file in [os.path.join(root, file) for file in files if ".wh." not in file]:
                    name = os.path.relpath(file, layer_directory)
                    if os.path.islink(file) and not os.path.exists(file):
                        missing = os.path.realpath(file)                        
                        resolved = self._find_file(directory, os.path.relpath(missing, layer_directory))
                        
                        shutil.copyfile(resolved, missing)

                        tar.add(resolved, arcname=os.path.relpath(missing, layer_directory))
                    tar.add(file, arcname=name)
        
        self.client.api.import_image(os.path.join(directory, "image.tar"), repository=self.image)

    def build_minimal_image(self):
        with TemporaryDirectory() as tmp:
            self._extract_image_in(tmp)
            self._extract_layers(tmp)
            self._materialize_last_layer(tmp)


            

