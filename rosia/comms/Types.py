from enum import Enum


class ClientType(str, Enum):
    SENDER = "sender"
    RECEIVER = "receiver"
