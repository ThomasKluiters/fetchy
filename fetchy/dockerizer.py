import docker
import logging

from io import BytesIO

from tqdm import tqdm

logger = logging.getLogger(__name__)


class Dockerizer(object):
    def __init__(self, tag, context):
        """
        The dockerizer will dockerize the downloaded packages into
        a docker image, fully wrapping the packages into a virtualized
        environment.

        Parameters
        ----------
        name : the name of the docker image

        context : the context in which to build the docker file
        """
        self.tag = tag
        self.context = context

    def build(self, binaries):
        path = ":".join(binaries)
        dockerfile = f"""
        FROM scratch
        ENV PATH {path}
        COPY . /
        """

        logger.info("Building image")
        with tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            miniters=1,
            total=3,
            desc=f"Building image {self.tag}",
        ) as t:

            with open(f"{self.context}/Dockerfile", "w", encoding="utf-8") as file:
                file.write(dockerfile)

            t.update(1)

            client = docker.DockerClient()

            t.update(1)

            response = client.images.build(path=self.context, tag=self.tag)

            t.update(1)

            logger.info(f"Built image {response}")
