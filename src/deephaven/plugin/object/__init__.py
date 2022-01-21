import abc
from typing import Optional, Union, Type

from .. import Plugin, Registration, register_all_into


class Reference:
    def __init__(self, index: int, type: Optional[str]):
        self._index = index
        self._type = type

    @property
    def index(self) -> int:
        return self._index

    @property
    def type(self) -> Optional[str]:
        return self._type


class Exporter(abc.ABC):
    @abc.abstractmethod
    def reference(self,
                  object,
                  allow_unknown_type: bool = False,
                  force_new: bool = False) -> Optional[Reference]:
        pass


class ObjectType(Plugin):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def is_type(self, object) -> bool:
        pass

    @abc.abstractmethod
    def to_bytes(self, exporter: Exporter, object) -> bytes:
        pass


def find_object_type(object) -> Optional[ObjectType]:
    class Visitor(Registration.Callback):
        def __init__(self) -> None:
            self._found = None

        def register(self, plugin: Union[Plugin, Type[Plugin]]) -> None:
            if self._found:
                return
            if isinstance(plugin, type):
                if not issubclass(plugin, ObjectType):
                    return
                plugin = plugin()
            if isinstance(plugin, ObjectType):
                if plugin.is_type(object):
                    self._found = plugin

        @property
        def found(self) -> Optional[ObjectType]:
            return self._found
    visitor = Visitor()
    register_all_into(visitor)
    return visitor.found
