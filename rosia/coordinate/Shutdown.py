from rosia.time import Time, never
import rosia


def request_shutdown(delay: Time = never):
    rosia.node_runtime_instance.request_shutdown(delay)  # type: ignore
