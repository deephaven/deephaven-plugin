import abc
import pathlib
import typing

from . import Plugin


class JsType(Plugin):
    """A javascript type plugin. Useful for adding custom javascript code to the server."""

    @abc.abstractmethod
    def distribution_path(self) -> typing.Generator[pathlib.Path, None, None]:
        """A generator that yields the distribution path directory."""
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The plugin name"""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """The plugin version"""
        pass

    @property
    @abc.abstractmethod
    def main(self) -> str:
        """The main js file, the relative path with respect to distribution_path."""
        pass

    def __str__(self) -> str:
        return f"{self.name}@{self.version}"
