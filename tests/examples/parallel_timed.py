from rosia import InputPort, OutputPort, reaction, Node, Coordinator
from rosia.time import Time, ms, s
from rosia.time.Timer import Timer
import logging


@Node
class IntGenerator:
    timer = InputPort[Time]()
    output = OutputPort[int]()

    def __init__(self):
        self.count = 0

    @reaction([timer])
    def generate(self):
        self.output(self.count)
        self.count += 1


@Node
class Printer:
    input_int1 = InputPort[int]()
    input_int2 = InputPort[int]()

    @reaction([input_int1, input_int2])
    def print_message(self):
        assert self.input_int1 == self.input_int2, (
            "Input ports should have the same value"
        )
        print(f"Received message: {self.input_int1} {self.input_int2}")


if __name__ == "__main__":
    coor = Coordinator(logging.INFO)
    timer1 = coor.create_node(Timer(interval=1 * ms, offset=0 * s))
    timer2 = coor.create_node(Timer(interval=1 * ms, offset=0 * s))
    int_gen1 = coor.create_node(IntGenerator())
    int_gen2 = coor.create_node(IntGenerator())
    printer = coor.create_node(Printer())
    timer1.output_timer >>= int_gen1.timer
    timer2.output_timer >>= int_gen2.timer
    int_gen1.output >>= printer.input_int1
    int_gen2.output >>= printer.input_int2

    print("Executing...")
    coor.execute()
