import pickle
from typing import Optional
from rosia.comms.serializers.base import SerializerBase
from rosia.comms.Types import ClientType


class Serializer(SerializerBase):
    def __init__(self, type: Optional[ClientType] = None):
        super().__init__(type)

    def serialize(self, obj) -> bytes:
        return pickle.dumps(obj)

    def deserialize(self, message: bytes):
        return pickle.loads(message)
