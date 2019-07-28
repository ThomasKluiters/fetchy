from fetchy import Fetchy, __version__

from .commands.blueprint import BlueprintCommand
from .commands.dockerize import DockerizeCommand

from fetchy.plugins import PackagesPlugin
from fetchy.plugins import PathsPlugin

from cleo import Application as BaseApplication


class FetchyApplication(BaseApplication):
    def __init__(self):
        super(FetchyApplication, self).__init__("Fetchy", __version__)
        self.fetchy = Fetchy()
        self.fetchy.register_plugin("packages", PackagesPlugin)
        self.fetchy.register_plugin("paths", PathsPlugin)
        self.add_commands(DockerizeCommand(), BlueprintCommand())
