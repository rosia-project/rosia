from rosia.frontend import (
    reaction as reaction,
    Node as Node,
    InputPort as InputPort,
    OutputPort as OutputPort,
)
from rosia.coordinate import Coordinator as Coordinator
from rosia.coordinate import request_shutdown as request_shutdown
from rosia.rerun import RerunManager as RerunManager
from rosia.logging import Logger as Logger
from rosia.utils import ObjectProxy as ObjectProxy
from typing import TYPE_CHECKING

rerun_manager = RerunManager()
log = logger = ObjectProxy(Logger())

if TYPE_CHECKING:
    log = logger = Logger()


# Monkey patches
node_runtime_instance = None
