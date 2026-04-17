import pytest

from rosia import InputPort, OutputPort, reaction, Node, Application
from rosia import request_shutdown, logical_time
from rosia.time import Time


@Node
class Counter:
    counter_in = InputPort[int]()
    counter_out = OutputPort[int]()

    def __init__(self):
        self.expected = 0

    def start(self):
        self.counter_out(0)

    @reaction([counter_in])
    def increment(self):
        assert self.counter_in == self.expected, f"Expected {self.expected} but got {self.counter_in}"
        expected_time = Time(0, microstep=self.expected + 1)
        assert logical_time() == expected_time, f"Expected {expected_time} but got {logical_time()}"
        self.expected += 1
        if self.counter_in >= 4:
            request_shutdown()
            return
        self.counter_out(self.counter_in + 1)


@pytest.mark.timeout(30)
def test_loop_logical():
    app = Application()
    counter = app.create_node(Counter())
    counter.counter_out.connect(counter.counter_in, delay=1)
    app.execute()


if __name__ == "__main__":
    test_loop_logical()
