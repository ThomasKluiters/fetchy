from fetchy import Fetchy, __version__

from .commands.download import DownloadCommand
from .commands.extract import ExtractCommand
from .commands.dockerize import DockerizeCommand

from cleo import Application as BaseApplication


class FetchyApplication(BaseApplication):
    def __init__(self):
        super(FetchyApplication, self).__init__("Fetchy", __version__)
        self.fetchy = Fetchy()
        self.add_commands(DownloadCommand(), ExtractCommand(), DockerizeCommand())
