import os

from fetchy.plugins import BasePlugin
from pathlib import Path


class PathsPlugin(BasePlugin):
    def __init__(self, data):
        super(PathsPlugin, self).__init__(
            "paths plugin",
            "paths",
            "A plugin that allows you to specify path variables.",
        )
        self.discover = data.get("discover", None)
        self.include = data.get("include", None)

    def validate(self):
        return True

    def _explore_directory(self, directory, context):
        root = Path(context.directory, directory)

        return set(
            [f"/{path.relative_to(root).as_posix()}/" for path in root.glob("**/bin")]
        )

    def _explore_path(self, context):
        paths = set(["/usr/bin/", "/bin/", "/sbin/", "/usr/sbin/"])

        return ":".join(paths)

    def build(self, context):
        context.dockerfile.env("PATH", self._explore_path(context))
        context.dockerfile.env("DEBIAN_FRONTEND", "noninteractive")

    def run(self, context):
        pass