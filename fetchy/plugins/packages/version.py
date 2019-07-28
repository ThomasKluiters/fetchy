def version_from_string(string):
    """Function for parsing a Version Object

    Versions are formatted in the following format:
    `[epoch:]upstream_version[-debian_revision]`.

    This function will attempt to parse such strings
    into a Version Object.
    """
    left = string.find(":")
    if left == -1:
        left = 0

    right = string.rfind("-")
    if right == -1:
        right = len(string)

    epoch, upstream, debian = (
        string[0:left],
        string[left:right].lstrip(":"),
        string[right : len(string)].lstrip("-"),
    )

    if epoch == "":
        epoch = 0
    else:
        epoch = int(epoch)

    if debian == "":
        debian = "0"

    return Version(upstream, debian, epoch)


class Version(object):
    def __init__(self, upstream_version, debian_revision=None, epoch=None):
        """A Version Object

        A version object holds the information
        required to identify a version of a package.

        Versions are stored in the following format:
        `[epoch:]upstream_version[-debian_revision]`.

        Both the epoch and debian version are optional.
        """
        if debian_revision is None:
            debian_revision = "0"
        if epoch is None:
            epoch = 0

        self.upstream_version = upstream_version
        self.debian_revision = debian_revision
        self.epoch = epoch

    def __str__(self):
        return f"{self.epoch}:{self.upstream_version}-{self.debian_revision}"
