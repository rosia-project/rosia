from rosia import InputPort, OutputPort, reaction, Node, Coordinator
import time


@Node
class StringGenerator:
    output_str = OutputPort[str]()

    def __init__(self, multiplier: int):
        print(f"StringGenerator initializing with multiplier: {multiplier}")
        self.multiplier = multiplier
        self.count = 0

    def start(self):
        while True:
            string = f"Hello, ROSIA! {self.count * self.multiplier}"
            print("Sending:", string)
            self.output_str(string)
            self.count += 1
            time.sleep(1)


@Node
class Printer:
    input_str = InputPort[str]()

    @reaction([input_str])
    def print_message(self):
        print(f"Received message: {self.input_str}")


if __name__ == "__main__":
    coor = Coordinator()
    str_gen = coor.create_node(StringGenerator(multiplier=2))
    printer = coor.create_node(Printer())
    str_gen.output_str >>= printer.input_str
    print("Executing")
    coor.execute()
