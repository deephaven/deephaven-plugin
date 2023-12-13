import abc
import pathlib
import typing

from . import Plugin


class JsPlugin(Plugin):
    """
    A JS plugin is a Plugin that allows adding javascript code under the server's URL path "js-plugins/".
    See https://github.com/deephaven/deephaven-plugins#js-plugins for more details about the underlying
    construction for JS plugins.
    """

    @abc.abstractmethod
    def path(self) -> pathlib.Path:
        """
        The directory path of the resources to serve. The path must exist.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        The JS plugin name. The JS plugin contents will be served via the URL path "js-plugins/{name}/",
        as well as included as the "name" field for the manifest entry in "js-plugins/manifest.json".
        """
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """
        The JS plugin version. Will be included as the "version" field for the manifest entry in
        js-plugins/manifest.json".
        """
        pass

    @property
    @abc.abstractmethod
    def main(self) -> str:
        """
        The main JS file path, specified relative to root. The main JS file must exist. Will be included
        as the "main" field for the manifest entry in "js-plugins/manifest.json".
        """
        pass

    def __str__(self) -> str:
        return f"{self.name}@{self.version}"
