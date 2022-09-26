import abc
from typing import Optional, Union, Type

from . import Plugin, Registration, register_all_into


class Reference:
    """A reference."""

    def __init__(self, index: int, type: Optional[str]):
        self._index = index
        self._type = type

    @property
    def index(self) -> int:
        """The index, which is defined by the order in which references are created.
        May be used in the output stream to refer to the reference from the client."""
        return self._index

    @property
    def type(self) -> Optional[str]:
        """The type."""
        return self._type


class Exporter(abc.ABC):
    """The interface for creating new references during ObjectType.to_bytes."""

    @abc.abstractmethod
    def reference(
        self, object, allow_unknown_type: bool = False, force_new: bool = False
    ) -> Optional[Reference]:
        """Gets the reference for object if it has already been created and force_new is False,
        otherwise creates a new one. If allow_unknown_type is False, and no type can be found, no
        reference will be created."""
        pass


class ObjectType(Plugin):
    """An object type plugin. Useful for serializing custom objects between the server / client."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the object type."""
        pass

    @abc.abstractmethod
    def is_type(self, object) -> bool:
        """Returns true if, and only if, the object is compatible with this object type."""
        pass

    @abc.abstractmethod
    def to_bytes(self, exporter: Exporter, object) -> bytes:
        """Serializes object into bytes. Must only be called with a compatible object."""
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
