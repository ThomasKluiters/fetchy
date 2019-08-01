import tempfile

from .context import Context
from .dockerfile import DockerFile

from logging import Logger

logger = Logger(__name__)


class BluePrint(object):
    def __init__(self, distribution, codename, architecture, tag, base, plugins):
        self.distribution = distribution
        self.architecture = architecture
        self.codename = codename
        self.base = base
        self.tag = tag
        self.plugins = plugins

    def _create_context(self):
        directory = "context"
        dockerfile = DockerFile(directory, self.base, self.tag)
        return Context(directory, dockerfile)

    def dockerize(self):
        for plugin in self.plugins:
            plugin.register(self)
        for plugin in self.plugins:
            if not plugin.validate():
                logger.error(f"{plugin.name} failed validation phase.")
                return

        with self._create_context() as context:
            for plugin in self.plugins:
                plugin.build(context)

            context.dockerfile.build()
            context.dockerfile.flatten()

            return {"tag": self.tag}
