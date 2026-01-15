from rosia import InputPort, OutputPort, reaction, Node, Coordinator
import time


@Node
class IntGenerator:
    output = OutputPort[int]()
    count = 0

    def start(self):
        while True:
            print(f"IntGenerator sending: {self.count}")
            self.output(self.count)
            self.count += 1
            time.sleep(1)


@Node
class Doubler:
    input_port = InputPort[int]()
    output_port = OutputPort[int]()

    @reaction([input_port])
    def process_input(self):
        input_value = self.input_port
        output_value = input_value * 2
        self.output_port(output_value)


@Node
class Printer:
    input_int = InputPort[int]()

    @reaction([input_int])
    def print_message(self):
        print(f"Received message: {self.input_int}")


if __name__ == "__main__":
    print("Setting up")
    coor = Coordinator()
    int_gen = coor.create_node(IntGenerator())
    printer = coor.create_node(Printer())
    doubler = coor.create_node(Doubler())
    int_gen.output >>= doubler.input_port
    doubler.output_port >>= printer.input_int

    print("Executing...")
    coor.execute()
