import cloudpickle
from typing import Optional
from rosia.comms.serializers.base import SerializerBase
from rosia.comms.Types import ClientType


class Serializer(SerializerBase):
    def __init__(self, type: Optional[ClientType] = None):
        super().__init__(type)

    def serialize(self, obj) -> bytes:
        return cloudpickle.dumps(obj, protocol=5)

    def deserialize(self, message: bytes):
        return cloudpickle.loads(message)
