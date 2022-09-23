import abc
import pathlib
import typing

from . import Plugin


class JsType(Plugin):
    @abc.abstractmethod
    def path(self) -> typing.Generator[pathlib.Path, None, None]:
        pass
