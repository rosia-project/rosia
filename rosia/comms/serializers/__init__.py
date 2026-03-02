from typing import Type

from rosia.comms.serializers.base import SerializerBase as SerializerBase
from rosia.comms.serializers.cloudpickle import Serializer as CloudpickleSerializer

Serializer: Type[SerializerBase] = CloudpickleSerializer
