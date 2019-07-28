import os
import docker


class Step(object):
    def __str__(self):
        raise NotImplementedError()


class FromStep(object):
    def __init__(self, image):
        self.image = image

    def __str__(self):
        return f"FROM {self.image}"


class CopyStep(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def __str__(self):
        return f"COPY {self.source} {self.destination}"


class EnvStep(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"ENV {self.name} {self.value}"


class DockerFile(object):
    def __init__(self, path, base, tag):
        self.path = path
        self.base = base
        self.tag = tag
        self.steps = []

        self.from_image(base)

    def step(self, step):
        self.steps.append(step)
        return self

    def from_image(self, name):
        return self.step(FromStep(name))

    def copy(self, source, destination):
        return self.step(CopyStep(source, destination))

    def env(self, name, value):
        return self.step(EnvStep(name, value))

    def create(self):
        with open(os.path.join(self.path, "Dockerfile"), "w", encoding="utf-8") as file:
            file.write("\n".join(map(str, self.steps)))

    def build(self):
        self.create()

        client = docker.DockerClient()
        client.images.build(path=self.path, tag=self.tag)
