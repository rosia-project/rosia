from abc import ABC, abstractmethod
from typing import Any, Type

from rosia.comms.Types import ClientType

from ..serializers.base import SerializerBase


class TransportBase(ABC):
    def __init__(
        self,
        type: ClientType,
        serializer: Type[SerializerBase],
        *args,
        **kwargs,
    ):
        self.endpoint: str

    @abstractmethod
    def send(self, msg: Any):
        """Send a message through the transport."""

    @abstractmethod
    def receive(self) -> Any:
        """Receive an already available message from the transport. Returns None if no message is available."""

    @abstractmethod
    def wait_for_message(self) -> None:
        """Wait for a message to be available on the transport. Blocks until a message is available.

        This method does not return or consume the message. Use receive() to get the message.
        """

    @abstractmethod
    def close(self):
        """Close the transport."""
