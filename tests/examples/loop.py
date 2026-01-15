from rosia import InputPort, OutputPort, reaction, Node, Coordinator
import time


@Node
class Worker:
    input_int = InputPort[int]()
    output_int = OutputPort[int]()

    def start(self):
        self.output_int(0)

    @reaction([input_int])
    def forward(self):
        print(f"Worker received message: {self.input_int}")
        self.output_int(self.input_int)
        time.sleep(1)


@Node
class Manager:
    input_int = InputPort[int]()
    output_int = OutputPort[int]()

    @reaction([input_int])
    def forward(self):
        self.output_int(self.input_int + 1)


if __name__ == "__main__":
    coor = Coordinator()
    worker = coor.create_node(Worker())
    manager = coor.create_node(Manager())
    worker.output_int >>= manager.input_int
    manager.output_int >>= worker.input_int
    coor.execute()
