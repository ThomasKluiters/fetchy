import shutil

class Context(object):
    def __init__(self, directory, dockerfile):
        self.directory = directory
        self.dockerfile = dockerfile

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # shutil.rmtree(self.directory)
        return
