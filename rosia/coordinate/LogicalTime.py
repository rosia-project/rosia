from rosia.time import Time
import rosia


def logical_time() -> Time:
    return rosia.node_runtime_instance.logical_time  # type: ignore
