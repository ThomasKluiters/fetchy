from cleo import Command


class FetchyCommandBase(Command):
    @property
    def fetchy(self):
        return self.application.fetchy
