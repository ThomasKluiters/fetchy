import docker
import logging

from io import BytesIO

from tqdm import tqdm

logger = logging.getLogger(__name__)


class Dockerizer(object):
    def __init__(self, tag, context, base=None):
        """
        The dockerizer will dockerize the downloaded packages into
        a docker image, fully wrapping the packages into a virtualized
        environment.

        Parameters
        ----------
        name : the name of the docker image

        context : the context in which to build the docker file
        
        base : the base image to use, defaults to `scratch`
        """
        if base is None:
            base = "scratch"
        self.tag = tag
        self.context = context
        self.base = base

    def build(self, binaries):
        path = ":".join(binaries)
        dockerfile = f"""
        FROM {self.base}
        ENV PATH {path}
        COPY . /
        """

        logger.info("Building image")
        with tqdm(total=3, desc=f"Building image {self.tag}") as t:
            with open(f"{self.context}/Dockerfile", "w", encoding="utf-8") as file:
                file.write(dockerfile)

            t.update(1)

            client = docker.DockerClient()

            t.update(1)

            response = client.images.build(path=self.context, tag=self.tag)

            t.update(1)
        return self.tag
