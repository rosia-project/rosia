from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from rosia.time import Time


T = TypeVar("T")


@dataclass
class MessageBase(Generic[T]):
    timestamp: Optional[Time]
    pass


@dataclass
class Message(MessageBase[T]):
    STAT: Optional[Time]
    data: T
    from_port: str
    to_port: str

    def __str__(self) -> str:
        return f"Message(timestamp={self.timestamp}, STAT={self.STAT}, data={self.data}, from_port={self.from_port}, to_port={self.to_port})"


@dataclass
class NodeRequestShutdownMessage(MessageBase):
    status_code: int


@dataclass
class NodeForceShutdownRequest(MessageBase):
    status_code: int


@dataclass
class ApplicationRequestShutdownMessage(MessageBase):
    pass


@dataclass
class ApplicationShutdownResponseMessage(MessageBase):
    pass


@dataclass
class ShutdownMessage(MessageBase):
    pass


@dataclass
class ExitMessage(MessageBase):
    node_name: str


@dataclass
class NoMoreMessage(MessageBase):
    from_port: str
    to_port: str
