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
        self, obj: object, allow_unknown_type: bool = False, force_new: bool = False
    ) -> Optional[Reference]:
        """Gets the reference for object if it has already been created and force_new is False,
        otherwise creates a new one. If allow_unknown_type is False, and no type can be found, no
        reference will be created."""
        pass


class MessageSender(Exporter):
    """The interface for creating references and sending messages for bidirectional communication"""

    @abc.abstractmethod
    def send_message(self, message: bytes) -> None:
        """Sends a message to the client"""
        pass


class ObjectType(Plugin):
    """An object type plugin. Useful for serializing custom objects between the server / client."""

    _message_sender: Union[MessageSender, None]

    def __init__(self):
        self._message_sender = None

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the object type."""
        pass

    @abc.abstractmethod
    def is_type(self, obj: object) -> bool:
        """Returns true if, and only if, the object is compatible with this object type."""
        pass

    @abc.abstractmethod
    def to_bytes(self, exporter: Exporter, obj: object) -> bytes:
        """Serializes object into bytes. Must only be called with a compatible object."""
        pass

    def supports_bidi_messaging(self, obj: object) -> bool:
        """Checks if an object supports bidirectional messaging
        Default implementation checks if the object descends from BidiObjectBase
        """
        return isinstance(obj, BidiObjectBase)

    def add_message_sender(self, obj: object, sender: MessageSender) -> None:
        """Should NOT be called in Python. Used by server plugin adapter to pass the message sender to the object"""
        if isinstance(obj, BidiObjectBase):
            obj.add_message_sender(sender)

    def remove_message_sender(self, obj: object) -> None:
        """Should NOT be called in Python. Used by server plugin adapter to remove the message sender from the object"""
        if isinstance(obj, BidiObjectBase):
            obj.remove_message_sender()

    def handle_message(self, message: bytes, obj: object, objects: list[object]) -> None:
        """Called when the client sends a message to the plugin.
        This default implementation delegates the message to the object the client specified
        """
        if isinstance(obj, BidiObjectBase):
            obj.handle_message(message, objects)


class BidiObjectBase:
    """Base class for an object which supports bidirectional streaming

    Any other implementations must extend this base class so the server knows the object supports bidi communication
    """
    _dh_message_sender: Union[MessageSender, None]

    def __init__(self):
        self._dh_message_sender = None

    @abc.abstractmethod
    def handle_message(self, message: bytes, objects: list[object]) -> None:
        """Used to handle messages sent by the client to the plugin

        Args:
            message (bytes): The message from the client. Unless the client specified otherwise, utf-8 encoded.
                May call decode on the message to get a string representation
            objects (list[object]): Any objects the client referenced in the message
        """
        pass

    def add_message_sender(self, sender: MessageSender):
        """Adds a message sender to this object."""
        self._dh_message_sender = sender

    def remove_message_sender(self):
        """Removes the message sender from this object."""
        self._dh_message_sender = None

    def reference(self, obj) -> Optional[Reference]:
        """Gets the export reference to a specific object.
        The reference index can be used in messages to the client to communicate about specific objects.
        Calling reference on an object that is not exported will queue it for export.
        The queued references will be sent to the client the next time send_message is called

        Args:
            obj (object): The object to reference

        Returns:
            The object reference for the object
        """
        if self._dh_message_sender:
            return self._dh_message_sender.reference(obj)

    def send_message(self, message: Union[str, bytes], encoding='utf-8') -> None:
        """Used to send a message to the client

        Args:
            message (Union[str, bytes]): The message to send to the client. If a string, it will be encoded to bytes
            encoding (str): The encoding to use for the message. Defaults to utf-8
        """
        if self._dh_message_sender:
            message_bytes = message if type(message) == bytes else str(message).encode(encoding=encoding)
            self._dh_message_sender.send_message(message_bytes)


def find_object_type(obj: object) -> Optional[ObjectType]:
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
                if plugin.is_type(obj):
                    self._found = plugin

        @property
        def found(self) -> Optional[ObjectType]:
            return self._found

    visitor = Visitor()
    register_all_into(visitor)
    return visitor.found
