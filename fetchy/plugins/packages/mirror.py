import locale
import validators


class Mirror(object):
    def __init__(self, locale):
        """
        A Mirror is an abstraction over a simple URL. A Mirror object
        should handle some other logic involved, such as finding an
        appropriate locale.

        Parameters
        ----------
        locale : a locale to use for finding an appropriate mirror, for example:
            the locale `nl` is used for the Netherlands.
        """
        self._locale = locale

    @property
    def locale(self):
        """
        Return the locale of this mirror, if none can be found attempt
        to fetch the mirror based on the current system.

        Returns
        -------
        locale : the locale the user specified, or a locale that was found
            when using the `locale` lib. If none can be found, None.
        """
        if self._locale:
            return self._locale

        (code, _) = locale.getdefaultlocale()
        if code is not None and "_" in code:
            return code.split("_")[0]
        return None

    def url(self):
        """
        The base url for this mirror. This URL should never be None
        and will be used as a fallback if the locale cannot be used.
        """
        raise NotImplementedError()

    def url_with_locale(self):
        """
        The base url for this mirror in which the locale is included
        this url may be None if no locale can be determined.
        """
        raise NotImplementedError()


class DirectMirror(Mirror):
    def __init__(self, url):
        """
        A DirecMirror is simply a URL supplied by the user, locales are not
        supported for this particular mirror as we have no knowledge of
        this structure of the URL.

        This does however, allow the user to use any mirror they want.

        Parameters
        ----------
        url : a url directly pointing to a mirror for a package manager
        """
        super(DirectMirror, self).__init__(None)
        self._url = url

        if not _url.endswith("/"):
            _url = url + "/"

    def url(self):
        return self._url

    def url_with_locale(self):
        return None


class UbuntuMirror(Mirror):
    def __init__(self, locale=None):
        """
        A UbuntuMirror is, as the class name may suggest, a mirror for ubuntu packages.

        This class will attempt to choose an appropriate mirror if the locale can be
        determined.

        Parameters
        ----------
        locale : a locale to use for finding an appropriate mirror, for example:
            the locale `nl` is used for the Netherlands.
        """
        super(UbuntuMirror, self).__init__(locale)

    def url(self):
        return "http://archive.ubuntu.com/ubuntu/"

    def url_with_locale(self):
        if self.locale:
            return f"http://{self.locale}.archive.ubuntu.com/ubuntu/"
        return None


class DebianMirror(Mirror):
    def __init__(self, locale=None):
        """
        A DebianMirror is, as the class name may suggest, a mirror for debian packages.

        This class will attempt to choose an appropriate mirror if the locale can be
        determined.

        Parameters
        ----------
        locale : a locale to use for finding an appropriate mirror, for example:
            the locale `nl` is used for the Netherlands.
        """
        super(DebianMirror, self).__init__(locale)

    def url(self):
        return "http://ftp.debian.org/debian/"

    def url_with_locale(self):
        if self.locale:
            return f"http://ftp.{self.locale}.debian.org/debian/"
        return None


class PersonalPackageArchiveMirror(Mirror):
    def __init__(self, url_or_name):
        """
        A Mirror instance for Personal Package Archives.

        Personal Package Archives don't have a mirror and are only supported
        for ubuntu.

        Parameters
        ----------
        url_or_name : either the name or url of a personal package archive
            the validators package is used to check if the given string
            is a valid url
        """
        super(PersonalPackageArchiveMirror, self).__init__(None)
        self.url_or_name = url_or_name

    def url(self):
        if validators.url(self.url_or_name):
            if not self.url_or_name.endswith("/"):
                return self.url_or_name + "/"
            return self.url_or_name

        return f"http://ppa.launchpad.net/{self.url_or_name}/ubuntu/"

    def url_with_locale(self):
        return None
