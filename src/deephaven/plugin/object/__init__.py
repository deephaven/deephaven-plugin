import abc
from typing import Optional, Union, Type

from .. import Plugin, Registration, register_all_into


def has_object_type_plugin(object) -> bool:
    class IsObjectType(Registration.Callback):
        def __init__(self) -> None:
            self._found = False

        def register(self, plugin: Union[Plugin, Type[Plugin]]) -> None:
            if self._found:
                return
            if isinstance(plugin, type):
                if not issubclass(plugin, ObjectType):
                    return
                plugin = plugin()
            if isinstance(plugin, ObjectType):
                self._found = plugin.is_type(object)

        @property
        def found(self) -> bool:
            return self._found
    visitor = IsObjectType()
    register_all_into(visitor)
    return visitor.found


class Reference:
    def __init__(self, index: int, type: Optional[str], ticket: bytes):
        self._index = index
        self._type = type
        self._ticket = ticket

    @property
    def index(self) -> int:
        return self._index

    @property
    def type(self) -> Optional[str]:
        return self._type

    @property
    def ticket(self) -> bytes:
        return self._ticket


class Exporter(abc.ABC):
    @abc.abstractmethod
    def reference(self, object) -> Reference:
        pass

    @abc.abstractmethod
    def new_reference(self, object) -> Reference:
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
