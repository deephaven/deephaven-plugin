import abc
import pathlib
import typing

from . import Plugin


class ContentPlugin(Plugin):
    """A content plugin. Useful for adding content the server that can be passed to a client."""

    @abc.abstractmethod
    def distribution_path(self) -> typing.Generator[pathlib.Path, None, None]:
        """A generator that yields the distribution path directory."""
        pass

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """The type of content."""
        pass

    @property
    @abc.abstractmethod
    def metadata(self):
        """The plugin metadata. Serialized to the client with `json.dumps`."""
        pass
