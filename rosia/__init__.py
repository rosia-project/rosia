from rosia.frontend import (
    reaction as reaction,
    Node as Node,
    InputPort as InputPort,
    OutputPort as OutputPort,
)
from rosia.coordinate import Application as Application
from rosia.coordinate import request_shutdown as request_shutdown

from rosia.rerun import RerunManager as RerunManager
from rosia.logging import Logger as Logger
from rosia.utils import ObjectProxy as ObjectProxy, FunctionProxy as FunctionProxy
from typing import TYPE_CHECKING
from rosia.time import Time

rerun_manager = RerunManager()
log = logger = ObjectProxy(Logger(), module="rosia", attr="logger")


def _advance_logical_time_unset(amount: "Time") -> None:
    raise RuntimeError(
        "advance_logical_time can only be called from within a node reaction"
    )


advance_logical_time = FunctionProxy(
    _advance_logical_time_unset, module="rosia", attr="advance_logical_time"
)

if TYPE_CHECKING:
    log = logger = Logger()

    def advance_logical_time(amount: Time) -> None: ...


# Monkey patches
node_runtime_instance = None  # type: ignore

if TYPE_CHECKING:
    from rosia.coordinate.Node import NodeRuntime

    node_runtime_instance: "NodeRuntime"
