---
sidebar_position: 3
---

## Naive program

Let's write a program that generates and prints numbers using timers.

First, write a node that generates numbers:

```python
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
            time.sleep(1)
```

Output ports are declared with `<output_port> = OutputPort[<type>]()`. `__init__` initializes the node, and `start` automatically runs after all nodes are initialized.

```python
@Node
class Printer:
    input_int = InputPort[int]()
    @reaction([input_int])
    def print_message(self):
        print(f"Received: {self.input_int}")
```

This nodes prints the numbers. Input ports are declared with `<input_port> = InputPort[<type>]()`. The received message can be referenced by `self.<input_port>`.

With the `@reaction` decorator, every time the input port `self.input_int` receives a message, the `print_message` method is executed.

To connect the two nodes, use a coordinator and create nodes within the coordinator. Connect ports using the `>>=` operator. Each node is a separate process for true concurrency.

```python
app = Application()
int_gen = app.create_node(IntGenerator())
printer = app.create_node(Printer())
int_gen.output_int >>= printer.input_int
app.execute()
```

Nodes initialize and run after `app.execute()` is called. Run this example with `python tests/examples/easy.py`.

### Time and synchronization

Let's modify the int generator to be triggered by a timer.

```python
@Node
class IntGenerator(Rosia):
    timer = InputPort[Time]()
    output = OutputPort[int]()

    def __init__(self):
        self.count = 0

    @reaction([timer])
    def generate(self):
        self.output(self.count)
        self.count += 1
```

and the printer to print two numbers from two input ports.

```python
@Node
class Printer:
    input_int1 = InputPort[int]()
    input_int2 = InputPort[int]()

    @reaction([input_int1, input_int2])
    def print_message(self):
        print(f"Received message: {self.input_int1} {self.input_int2}")
```

We can create two instances of `IntGenerator` in a coordinator:

```python
app = Application(logging.INFO)
timer1 = app.create_node(Timer(interval=1 * ms, offset=0 * s))
timer2 = app.create_node(Timer(interval=1 * ms, offset=0 * s))
int_gen1 = app.create_node(IntGenerator())
int_gen2 = app.create_node(IntGenerator())
printer = app.create_node(Printer())
timer1.output_timer >>= int_gen1.timer
timer2.output_timer >>= int_gen2.timer
int_gen1.output >>= printer.input_int1
int_gen2.output >>= printer.input_int2

app.execute()
```

When we execute this example with `python tests/examples/parallel_timed.py`, notice how the two inputs are always synchronized since the timers are aligned. Rosia handles synchronization internally so you don't have to worry about it!

# Synchronization

This tutorial shows how Rosia automatically synchronizes messages from multiple sources. When two messages arrive at the same logical time, they are processed together in a single reaction.

## Pipeline

```
Timer -> IntGenerator1 -+-> Printer
Timer -> IntGenerator2 -+
```

Two independent timers drive two generators. Both feed into a single `Printer` node with two input ports.

## Nodes

```python
from rosia import InputPort, OutputPort, reaction, Node, Application
from rosia import request_shutdown, log
from rosia.time import s, Time
from rosia.time.Timer import Timer


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

    def __init__(self):
        self.receive_count = 0

    @reaction([input_int1, input_int2])
    def print_message(self):
        log.info(f"Received: {self.input_int1}, {self.input_int2}")
        assert self.input_int1 == self.input_int2
        self.receive_count += 1
        if self.receive_count >= 3:
            request_shutdown(0 * s)
```

## Wiring

Both timers use the same interval and offset, so they fire at the same logical times.

```python
app = Application()
timer1 = app.create_node(Timer(interval=1 * s, offset=0 * s))
timer2 = app.create_node(Timer(interval=1 * s, offset=0 * s))
gen1 = app.create_node(IntGenerator())
gen2 = app.create_node(IntGenerator())
printer = app.create_node(Printer())

timer1.output_timer >>= gen1.timer
timer2.output_timer >>= gen2.timer
gen1.output >>= printer.input_int1
gen2.output >>= printer.input_int2

app.execute()
```

Output:

```
Received: 0, 0
Received: 1, 1
Received: 2, 2
```

## How synchronization works

Both generators send at the same logical timestamp (driven by timers with the same interval). Rosia's event queue merges messages at the same timestamp into a single event. The `Printer`'s reaction fires once per timestamp with both values
available.

This happens automatically — no manual synchronization is needed. Even if one generator is physically slower than the other, Rosia waits until all messages for a timestamp have arrived before triggering the reaction.

## Port value retention

Input ports retain their most recent value. If a reaction is triggered by one port, the other port still holds its previous value:

```python
@reaction([input_int1, input_int2])
def print_message(self):
    # Both ports are always readable, even if only one
    # received a new message in this event
    log.info(f"{self.input_int1}, {self.input_int2}")
```
