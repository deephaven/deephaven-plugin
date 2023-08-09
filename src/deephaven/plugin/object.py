import abc
from typing import Optional, Union, Type, List, Any

from . import Plugin, Registration, register_all_into

"""
Tools to create ObjectType plugins in Python to run on a Deephaven server.
"""


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
        """Creates a reference for an object, ensuring that it is exported for use on the client. Each time this is
        called, a new reference will be returned, with the index of the export in the data to be sent to the client.
        """
        pass


class MessageStream(abc.ABC):
    """A stream of messages, either sent from server to client or client to server. ObjectType implementations
    provide an instance of this interface for each incoming stream to invoke as messages arrive, and will
    likewise be given an instance of this interface to be able to send messages to the client.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    def on_close(self) -> None:
        """Closes the stream on both ends. No further messages can be sent or received."""
        pass

    @abc.abstractmethod
    def on_data(self, payload: bytes, references: List[Any]) -> None:
        """Transmits data to the remote end of the stream. This can consist of a binary payload and references to
        objects on the server.
        """
        pass


class ObjectType(Plugin):
    """An object type plugin. Useful for serializing custom objects between the server / client."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the object type."""
        pass

    @abc.abstractmethod
    def is_type(self, obj: Any) -> bool:
        """Returns True if, and only if, the object is compatible with this object type."""
        pass


class BidirectionalObjectType(ObjectType):
    """Base class for an object type that can continue to send responses to the client, or receive requests
    from the server even after it is fetched.
    """

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
        """Serializes obj into bytes. Must only be called with a compatible object."""
        pass
