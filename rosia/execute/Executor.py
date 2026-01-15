from rosia.comms.Types import ClientType
from rosia.comms.transports import Transport, TransportBase
from rosia.comms.serializers import Serializer, SerializerBase
from typing import Optional, Type, Any
import multiprocessing
import time
import inspect


def _worker_process(
    cls: Type[Any],
    endpoint_queue: multiprocessing.Queue,
    response_endpoint: str,
    serializer: Type[SerializerBase],
    serialized_instance: Optional[bytes],
):
    if serialized_instance is not None:
        serializer_instance = serializer(ClientType.RECEIVER)
        instance = serializer_instance.deserialize(serialized_instance)
    else:
        instance = None

    request_receiver = Transport(ClientType.RECEIVER, serializer, "")

    request_endpoint = request_receiver.endpoint

    endpoint_queue.put(request_endpoint)

    response_sender = Transport(ClientType.SENDER, serializer, response_endpoint)

    try:
        while True:
            request_receiver.wait_for_message()
            request = request_receiver.receive()

            if request is None:
                continue

            if request == "__SHUTDOWN__":
                break

            method_name = request["method_name"]
            args = request.get("args", ())
            kwargs = request.get("kwargs", {})

            try:
                if method_name == "__init__":
                    if instance is not None:
                        raise RuntimeError("Instance already initialized")
                    instance = cls(*args, **kwargs)
                    response = {"success": True, "result": None}
                else:
                    if instance is None:
                        raise RuntimeError(
                            "Instance not initialized. Call __init__ first or pass an initialized instance."
                        )
                    method = getattr(instance, method_name)
                    result = method(*args, **kwargs)
                    response = {"success": True, "result": result}
            except Exception as e:
                response = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

            response_sender.send(response)

    finally:
        request_receiver.close()
        response_sender.close()


class Executor:
    def __init__(
        self,
        cls_or_instance: Any,
        type: Optional[ClientType] = None,
        transport: Optional[TransportBase] = None,
        serializer: Optional[Type[SerializerBase]] = None,
    ):
        if serializer is None:
            serializer = Serializer

        is_instance = not inspect.isclass(cls_or_instance)

        if is_instance:
            self.cls = cls_or_instance.__class__
            serializer_instance = serializer(ClientType.SENDER)
            serialized_instance = serializer_instance.serialize(cls_or_instance)
        else:
            self.cls = cls_or_instance
            serialized_instance = None

        self.response_receiver = Transport(ClientType.RECEIVER, serializer, "")
        time.sleep(0.1)
        response_endpoint = self.response_receiver.endpoint

        endpoint_queue = multiprocessing.Queue()

        self.worker_process = multiprocessing.Process(
            target=_worker_process,
            args=(
                self.cls,
                endpoint_queue,
                response_endpoint,
                serializer,
                serialized_instance,
            ),
        )
        self.worker_process.start()

        request_endpoint = endpoint_queue.get(timeout=5.0)

        self.request_sender = Transport(ClientType.SENDER, serializer, request_endpoint)
        time.sleep(0.1)

        self.serializer = serializer

    def call(self, method_name: str, *args, **kwargs) -> Any:
        request = {"method_name": method_name, "args": args, "kwargs": kwargs}
        self.request_sender.send(request)

        self.response_receiver.wait_for_message()
        response = self.response_receiver.receive()

        if response is None:
            raise RuntimeError("No response received from worker process")

        if not response.get("success", False):
            error_type_name = response.get("error_type", "Exception")
            error_msg = response.get("error", "Unknown error")
            try:
                import builtins

                exc_class = getattr(builtins, error_type_name, None)
                if exc_class is None or not issubclass(exc_class, Exception):
                    raise ValueError()
                raise exc_class(error_msg)
            except (ValueError, AttributeError, TypeError):
                raise RuntimeError(f"{error_type_name}: {error_msg}")

        return response.get("result")

    def call_no_ret(self, method_name: str, *args, **kwargs) -> None:
        """Synchronously send a request without waiting for a response."""
        request = {"method_name": method_name, "args": args, "kwargs": kwargs}
        self.request_sender.send(request)

    def shutdown(self):
        if self.worker_process.is_alive():
            self.request_sender.send("__SHUTDOWN__")
            self.worker_process.join()

        self.request_sender.close()
        self.response_receiver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False
