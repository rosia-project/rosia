from dataclasses import dataclass
from typing import Generic, TypeVar

from rosia.time import Time


T = TypeVar("T")


@dataclass
class MessageBase(Generic[T]):
    timestamp: Time
    pass


@dataclass
class Message(MessageBase[T]):
    next_timestamp: Time
    data: T
    from_port: str
    to_port: str

    def __str__(self) -> str:
        return f"Message(timestamp={self.timestamp}, next_timestamp={self.next_timestamp}, data={self.data}, from_port={self.from_port}, to_port={self.to_port})"


@dataclass
class CoordinatorShutdownRequestMessage(MessageBase):
    status_code: int


@dataclass
class ShutdownMessage(MessageBase):
    timestamp: Time
    pass
