from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from rosia.time import Time


T = TypeVar("T")


@dataclass
class MessageBase(Generic[T]):
    next_timestamp: Optional[Time]
    timestamp: Optional[Time]


@dataclass
class Message(MessageBase[T]):
    data: T
    from_port: str
    to_port: Optional[str] = None

    def __str__(self) -> str:
        return f"Message(timestamp={self.timestamp}, next_timestamp={self.next_timestamp}, data={self.data}, from_port={self.from_port}, to_port={self.to_port})"
