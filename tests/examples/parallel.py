from rosia import InputPort, OutputPort, reaction, Node, Coordinator
import time


@Node
class IntGenerator:
    output = OutputPort[int]()

    def __init__(self):
        self.count = 1

    @reaction([])
    def start(self):
        while True:
            self.output(self.count)
            self.count += 1
            time.sleep(0.01)


@Node
class Printer:
    input_int1 = InputPort[int]()
    input_int2 = InputPort[int]()

    @reaction([input_int1, input_int2])
    def print_message(self):
        print(f"Received message: {self.input_int1} {self.input_int2}")
        assert self.input_int1 == self.input_int2


if __name__ == "__main__":
    print("Setting up")
    coor = Coordinator()
    int_gen1 = coor.create_node(IntGenerator())
    int_gen2 = coor.create_node(IntGenerator())
    printer = coor.create_node(Printer())
    int_gen1.output >>= printer.input_int1
    int_gen2.output >>= printer.input_int2

    print("Executing...")
    coor.execute()
