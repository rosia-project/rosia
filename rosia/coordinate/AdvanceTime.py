from rosia.time import Time
import rosia


def advance_time(delta: Time):
    rosia.node_runtime_instance.advance_time(delta)
