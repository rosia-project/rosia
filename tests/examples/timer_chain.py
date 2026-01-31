from rosia import InputPort, OutputPort, reaction, Node, Coordinator
from rosia.time import Time, s
from rosia.time.Timer import Timer


@Node
class IntGenerator:
    input_port = InputPort[Time]()
    output_port = OutputPort[Time]()

    def __init__(self):
        self.number = 0

    @reaction([input_port])
    def process_input(self):
        self.output_port(self.input_port)
        self.number += 1


@Node
class Printer:
    input_timer = InputPort[Time]()

    @reaction([input_timer])
    def print_message(self):
        print(f"Received message: {self.input_timer}")


if __name__ == "__main__":
    coor = Coordinator()
    timer_node = coor.create_node(Timer(interval=1 * s, offset=0 * s))
    int_generator = coor.create_node(IntGenerator())
    printer = coor.create_node(Printer())
    timer_node.output_timer >>= int_generator.input_port
    int_generator.output_port >>= printer.input_timer

    coor.execute()
