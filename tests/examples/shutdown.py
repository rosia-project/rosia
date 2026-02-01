from rosia import InputPort, OutputPort, reaction, Node, Coordinator
import time

from rosia import request_shutdown
from rosia.time import s


@Node
class IntGenerator:
    output_int = OutputPort[int]()

    def __init__(self):
        self.count = 0

    def start(self):
        while True:
            print("Sending:", self.count)
            self.output_int(self.count)
            self.count += 1
            if self.count > 2:
                request_shutdown(0 * s)
                print("Shutting down")
                break
            time.sleep(1)


@Node
class Printer:
    input_int = InputPort[int]()

    @reaction([input_int])
    def print_message(self):
        print(f"Received: {self.input_int}")


if __name__ == "__main__":
    coor = Coordinator()
    int_gen = coor.create_node(IntGenerator())
    printer = coor.create_node(Printer())
    int_gen.output_int >>= printer.input_int

    coor.execute()
