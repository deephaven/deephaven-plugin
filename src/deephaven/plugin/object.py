import abc
from typing import Optional, Union, Type, List, Any

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


class Exporter(abc.ABC):
    """The interface for creating new references during FetchOnlyObjectBase.to_bytes."""

    @abc.abstractmethod
    def reference(self, obj: object) -> Reference:
        """Creates a reference for an object. Each reference """
        pass


class MessageStream(abc.ABC):
    """A stream of messages, either sent from server to client or client to server. ObjectType implementations
    provide an instance of this interface for each incoming stream to invoke as messages arrive, and will
    likewise be given an instance of this interface to be able to send messages to the client.
    """
    def __init__(self):
        pass

    @abc.abstractmethod
    def on_close(self):
        """Closes the stream on both ends. No further messages can be sent or received."""
        pass

    @abc.abstractmethod
    def on_data(self, payload: bytes, references: List[Any]):
        """Transmits data to the remote end of the stream. This can consist of a binary payload and references to
        objects on the server.
        """
        pass


class ObjectType(Plugin):
    """An object type plugin. Useful for serializing custom objects between the server / client."""

    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the object type."""
        pass

    @abc.abstractmethod
    def is_type(self, obj: Any) -> bool:
        """Returns True if, and only if, the object is compatible with this object type."""
        pass


class BidirectionObjectType(ObjectType):
    """Base class for an object type that can continue to send responses to the client, or receive requests
    from the server even after it is fetched.
    """
    def __init__(self):
        pass
    @abc.abstractmethod
    def create_client_connection(self, obj: object, connection: MessageStream) -> MessageStream:
        """Signals creation of a client stream to the specified object. The returned MessageStream implementation will
        be called with each received message from the client, and can call the provided connection parameter to send
        messages as needed to the client.

        Before returning, this method must call connection.on_message with some initial payload, so that the client has
        an initial view of the object.
        """
        pass


class FetchOnlyObjectType(ObjectType):
    """Base class for an object type which will only be fetched once, rather than support streaming requests or
    responses.
    """
    @abc.abstractmethod
    def to_bytes(self, exporter: Exporter, obj: Any) -> bytes:
        """Serializes object into bytes. Must only be called with a compatible object."""
        pass


def find_object_type(obj: Any) -> Optional[ObjectType]:
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
