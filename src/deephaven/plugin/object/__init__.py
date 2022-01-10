import abc

from .. import Plugin


class Reference:
    def __init__(self, id: bytes):
        self._id = id

    @property
    def id(self) -> bytes:
        return self._id


class Exporter(abc.ABC):
    @abc.abstractmethod
    def new_server_side_reference(self, object) -> Reference:
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
