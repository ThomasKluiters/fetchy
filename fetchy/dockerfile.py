import os
import docker


class Step(object):
    def __str__(self):
        raise NotImplementedError()


class RunStep(object):
    def __init__(self, script):
        self.script = script

    def __str__(self):
        script = ",".join(map(lambda x: f'"{x}"', self.script))
        return f"RUN [{script}]"


class CmdStep(object):
    def __init__(self, script):
        self.script = script

    def __str__(self):
        script = ",".join(self.script)
        return f"CMD [{script}]"


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
        self.client = docker.DockerClient()

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

    def cmd(self, script):
        return self.step(CmdStep(script))

    def run(self, script):
        return self.step(RunStep(script))

    def build(self):
        self.create()

        (img, _) = self.client.images.build(path=self.path)
        return img.short_id

