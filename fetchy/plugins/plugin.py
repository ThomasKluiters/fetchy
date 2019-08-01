import os


class BasePlugin(object):
    def __init__(self, name, hook, description):
        self.description = description
        self.name = name
        self.hook = hook
        self.blueprint = None

    def register(self, blueprint):
        self.blueprint = blueprint

    def _dir_name(self):
        return self.hook

    def _dir_in_context(self, context):
        return os.path.join(context.directory, self._dir_name())

    def validate(self):
        """
        Validate this plugin, ensuring that this plugin has
        all required information to run.

        Returns
        -------------------
        success : a boolean value indicating if validation is
            succesfull or not
        """
        raise NotImplementedError()

    def build(self, context):
        """
        Performs this plugins' build process, downloading files,
        manipulating the context.
        """
        raise NotImplementedError()
