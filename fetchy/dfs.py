import os
import json
import tarfile
import docker

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
            self.layers = map(lambda x: x.split("/")[0], json.loads(manifest.read())[0]["Layers"])

        for layer in self.layers:
            with tarfile.open(os.path.join(directory, layer, "layer.tar")) as layer_tar:
                layer_tar.extractall(directory, layer)

    def _find_file(self, directory, path):
        for layer in reversed(self.layers):
            path_in_layer = os.path.join(directory, layer, path)
            if os.path.isfile(path_in_layer):
                return path_in_layer
        print("Cannot find file.. :/")

    def _materialize_last_layer(self, directory):
        layer = self.layers[-1]

    def build_minimal_image(self):
        with TemporaryDirectory() as tmp:
            self._extract_image_in(tmp)
            self._extract_layers(tmp)


            

