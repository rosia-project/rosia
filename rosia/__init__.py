from rosia.frontend import (
    reaction as reaction,
    Node as Node,
    InputPort as InputPort,
    OutputPort as OutputPort,
)
from rosia.coordinate import Coordinator as Coordinator
from rosia.logging import logger as logger, log as log
from rosia.coordinate import request_shutdown as request_shutdown

# Monkey patches
node_runtime_instance = None
