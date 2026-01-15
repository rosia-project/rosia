from rosia import InputPort, reaction, Node, Coordinator
import time


@Node
class Printer:
    input_str = InputPort[str]()

    @reaction([input_str])
    def print_message(self):
        print(f"Received message: {self.input_str}")


if __name__ == "__main__":
    coor = Coordinator()
    printer = coor.create_node(Printer())

    print("Executing...")
    coor.execute()

    while True:
        coor.set_value(printer.input_str, "Hello, ROSIA!")
        time.sleep(1)
