import time

from rosia import InputPort, OutputPort, reaction, Node, Coordinator
from rosia import request_shutdown, log
from rosia.time import s


@Node
class Source:
    output = OutputPort[int]()

    def start(self):
        for i in range(3):
            self.output(i)
            time.sleep(0.01)
        request_shutdown(0 * s)


@Node
class Sink:
    input_port = InputPort[int]()

    @reaction([input_port])
    def on_input(self):
        log.warning(f"got {self.input_port}")


if __name__ == "__main__":
    coor = Coordinator()
    src = coor.create_node(Source())
    sink = coor.create_node(Sink())
    src.output >>= sink.input_port
    coor.execute()
