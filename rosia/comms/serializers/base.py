from typing import Optional, Any
from abc import ABC, abstractmethod
from rosia.comms.Types import ClientType


class SerializerBase(ABC):
    @abstractmethod
    def __init__(self, type: Optional[ClientType]):
        if type is not None and not isinstance(type, ClientType):
            raise ValueError(f"Invalid Serializer Type: {type}")
        self.type = type

    @abstractmethod
    def serialize(self, obj) -> bytes:
        pass

    @abstractmethod
    def deserialize(self, message: bytes) -> Any:
        pass
