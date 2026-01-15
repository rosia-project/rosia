from rosia.frontend import OutputPort, Node, Rosia
from rosia.time import Time
import time


@Node
class Timer(Rosia):
    output_timer = OutputPort[Time]()

    def __init__(self, interval: Time, offset: Time = Time(0)):
        self.interval = interval
        self.time_current = offset
        self.output_timer.set_next_timestamp(self.time_current)

    def start(self):
        while True:
            self.output_timer(
                self.time_current,
                timestamp=self.time_current,
                next_timestamp=self.time_current + self.interval,
            )
            self.time_current += self.interval
            time.sleep(self.interval.to_seconds())
