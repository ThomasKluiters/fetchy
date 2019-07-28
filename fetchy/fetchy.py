import yaml

from .blueprint import BluePrint

from logging import Logger

logger = Logger(__name__)


class Fetchy(object):
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, hook, plugin):
        self.plugins[hook] = plugin

    def blueprint_from_yaml(self, file):
        return self.blueprint_from_dict(self._load_yaml(file))

    def blueprint_from_dict(self, data):
        if "tag" not in data:
            raise ValueError("Tag must be supplied in blueprint.")
        if "distribution" not in data:
            raise ValueError("Distribution must be supplied in blueprint.")
        if "codename" not in data:
            raise ValueError("Codename must be supplied in blueprint.")
        if "architecture" not in data:
            raise ValueError("Architecture must be supplied in blueprint.")

        active_plugins = []

        for (key, value) in data.items():
            if key in ["distribution", "codename", "architecture", "tag", "base"]:
                continue
            if key not in self.plugins:
                logger.warn(f"The plugin {key} is not recognised and is skipped.")
                continue
            active_plugins.append(self.plugins[key](value))

        return BluePrint(
            data["distribution"],
            data["codename"],
            data["architecture"],
            data["tag"],
            data.get("base", "scratch"),
            active_plugins,
        )

    def _load_yaml(self, file):
        with open(file, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
