---
sidebar_position: 1
---

# Logical Time

In Rosia, _logical time_ is the timestamp system used for ordering and synchronization. It is up to you to control logical time within each node, and Rosia will take care of execution and synchronization across nodes.

Logical time is a monotonically increasing value. You can think of it as an order specification for messages and code execution. A message with a smaller logical time will be processed with a reaction before a message with a large logical
time.

Messages with the same logical time are considered simultaneous. As shown in example [Synchronization](../tutorial/synchronization), if multiple input ports have the same logical time, they will be synchronized to only trigger the reaction
once.

Each node has logical time `Time(0)` when `start()` is called at the beginning of execution. The logical time can be manipulated in `start()` and reactions marked with the `@reaction()` decorator in the following ways:

- `yield <Time>` pauses the current reaction, and resumes after the specified logical time interval. In the meantime, it will process other reactions.
- When a reaction is triggered by reacting to input ports defined in `@reaction(<ports>)`, the node will advance logical time to the logical time associated with the message received at the input port.

# Time Representation

Rosia is a variant of the [reactor model of computation](https://reactor-model.org/) and uses the discrete time model. In `rosia/time/Time.py`, all time values are represented by a int value. Each nanosecond is subdivided into
`TIME_DIVISOR = 1000` microsteps. Rosia provides built-in time units `s`, `ms`, `us` and `ns`:

- 1 `ns` = 1000 microsteps
- 1 `us` = 1000 `ns`
- 1 `ms` = 1000 `us`
- 1 `s` = 1000 `ms`

All time values are treated as intervals, so you can add, subtract and multiply time. For example, to denote an interval of 3 seconds, you can use `3 * s`.

There's also `never` that represents the smallest time value, and `forever` that represents the largest time value. Adding or subtracting time to `never` and `forever` will yield `never` or `forever`.
