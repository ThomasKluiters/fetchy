from .command import FetchyCommandBase


class BlueprintCommand(FetchyCommandBase):
    """
    Dockerize a blueprint into a docker image.

    blueprint
      {file        : the blueprint to dockerize}
    """

    def handle(self):
        file = self.argument("file")

        blueprint = self.fetchy.blueprint_from_yaml(file)
        result = blueprint.dockerize()

        self.line(f"Succesfully built image: `{result['tag']}`!")
