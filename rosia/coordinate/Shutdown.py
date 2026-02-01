from rosia.time import Time
import rosia


def request_shutdown(delay: Time = Time(0)):
    rosia.node_runtime_instance.request_shutdown(delay)  # type: ignore
