---
sidebar_position: 5
---

# Shutdown

There are two ways for a Rosia application to shut down:

1. **Automatic shutdown**: when all data has finished flowing through the graph, the application exits on its own.
2. **Explicit shutdown**: a node calls `request_shutdown()` to trigger a coordinated shutdown at a specific logical time.

## Automatic Shutdown (NoMoreMessage)

When a node has no more data to send — either because it's a source node whose `start()` returned with an empty event queue, or because all its upstream ports have signaled completion — it sends a `NoMoreMessage` on all its output ports.
This propagates downstream through the graph.

When a node detects that all of its upstream ports have sent `NoMoreMessage` and its event queue is empty, it propagates `NoMoreMessage` on its own output ports and exits.

This enables finite computations to exit cleanly without any explicit shutdown call:

```python
@Node
class Greeter:
    output = OutputPort[str]()

    def start(self):
        self.output("Hello, World!")
        # start() returns, Greeter has no input ports and no pending events,
        # so it automatically sends NoMoreMessage downstream
```

### Propagation rules

- **Source nodes** (no input ports): after `start()` returns, if the event queue is empty, send `NoMoreMessage` from all output ports.
- **Interior nodes**: when all upstream ports have sent `NoMoreMessage` and the event queue is empty, send `NoMoreMessage` from all output ports and exit.
- **Terminal nodes** (no output ports): when all upstream ports have sent `NoMoreMessage` and the event queue is empty, exit.

### Active upstream count

Each input port tracks an `active_upstream_count` — the number of upstream output ports that have not yet sent `NoMoreMessage`. This is initialized to the number of upstream connections during node setup. When a `NoMoreMessage` arrives, the
count is decremented. When all input ports have `active_upstream_count == 0`, the node is done.

## Explicit Shutdown (request_shutdown)

A node can trigger a coordinated shutdown by calling `request_shutdown()`:

```python
from rosia import request_shutdown
from rosia.time import s

request_shutdown()        # shut down as soon as possible
request_shutdown(1 * s)   # shut down 1 second from now (logical time)
```

When called with a delay, the node sends a `NodeRequestShutdownMessage` to the coordinator with the target shutdown timestamp (`logical_time + delay`). When called without arguments, the default delay is `never`, which signals the
coordinator to negotiate immediate shutdown — each node will shut down at its current logical time.

### Shutdown negotiation

The coordinator does not immediately shut down all nodes. Instead, it runs a negotiation protocol to ensure every node has a chance to finish processing up to a consistent logical time:

1. **Coordinator receives the request**: The first `NodeRequestShutdownMessage` from any node starts the negotiation. The coordinator records the requested shutdown timestamp.

2. **Coordinator asks all alive nodes**: An `ApplicationRequestShutdownMessage` is sent to every node that has not already exited. This message carries the proposed shutdown timestamp.

3. **Nodes respond**: Each node compares the proposed timestamp to its current logical time. If it has already advanced past the proposed time, it responds with its current logical time instead. The node also sets an internal
   `shutdown_time_barrier` so it will not advance further. The response is an `ApplicationShutdownResponseMessage`.

4. **Coordinator picks the final time**: The coordinator takes the maximum timestamp across all responses. This ensures no node is forced to roll back.

5. **Coordinator broadcasts `ShutdownMessage`**: The final shutdown timestamp is sent to all alive nodes.

6. **Nodes process remaining work**: Each node pushes a `ShutdownEvent` into its event queue at the final timestamp. The event loop continues processing events and reactions up to that time. When the `ShutdownEvent` is reached, the node
   calls `shutdown()` and exits.

### Shutdown barrier

During negotiation, each node sets `shutdown_time_barrier` to just past the agreed time. This value feeds into the STAT computation, preventing the node from advancing logical time beyond the shutdown point while still allowing it to finish
processing events at or before that time.

## Force Shutdown

If a node encounters an unrecoverable error, it sends a `NodeForceShutdownRequest` with a non-zero status code. The coordinator responds by:

1. Sending a `ShutdownMessage` with timestamp `never` to all alive nodes, causing immediate shutdown.
2. Waiting briefly for nodes to exit, then force-killing any that remain.
3. Exiting with the error status code.

A `KeyboardInterrupt` (Ctrl+C) in the main process also triggers this path, sending a `ShutdownMessage` with timestamp `never` to all nodes.

## Node cleanup

Regardless of how shutdown is triggered, each node runs the same cleanup sequence before exiting:

1. If the node defines a `shutdown()` method, it is called.
2. All transports (receiver, sender, coordinator) are closed.
3. The logger is flushed and shut down.
4. The process exits with the appropriate status code.
