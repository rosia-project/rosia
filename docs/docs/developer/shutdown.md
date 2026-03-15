---
sidebar_position: 5
---

# Shutdown

Shutdown in Rosia is a coordinated process. A node requests shutdown, the coordinator broadcasts the request to all nodes, and each node processes all events up to the shutdown timestamp before exiting.

## API

Any node can initiate shutdown by calling:

```python
from rosia import request_shutdown
from rosia.time import s

request_shutdown(delay=0 * s)
```

- `delay`: how far in the future (relative to the node's current logical time) the shutdown should occur. A delay of `0 * s` means shut down at the current logical time.

## Shutdown Sequence

```
Node                        Coordinator                     All Nodes
 │                               │                               │
 │  CoordinatorShutdownRequest   │                               │
 │  (timestamp, status_code)     │                               │
 │──────────────────────────────>│                               │
 │                               │       ShutdownMessage         │
 │                               │       (timestamp)             │
 │                               │──────────────────────────────>│
 │                               │                               │
 │                               │                          process remaining events
 │                               │                          then shutdown and exit
```

### 1. Node requests shutdown

When `request_shutdown(delay)` is called, the node computes `shutdown_timestamp = logical_time + delay` and sends a `CoordinatorShutdownRequestMessage` to the coordinator. The node does **not** shut down immediately — it continues
processing events.

### 2. Coordinator broadcasts

The coordinator waits for a shutdown request from any node. Upon receiving one, it sends a `ShutdownMessage` with the shutdown timestamp to **every** node (including the one that requested it).

If a `timeout` was passed to `Coordinator.execute(timeout=...)`, the coordinator will automatically initiate shutdown when the timeout expires, without waiting for a node to request it.

### 3. Nodes receive and process

Each node picks up the `ShutdownMessage` during `drain_message_queue()`. This pushes a `ShutdownEvent` to the event queue at the shutdown timestamp. The node does **not** stop immediately — it continues processing all data events that have
timestamps at or before the shutdown timestamp.

### 4. ShutdownEvent processed

When `advance_logical_time` pops the `ShutdownEvent` from the event queue, `shutdown_requested` is set to `True`. This causes the event loop to exit. The node then calls `node.shutdown()` (if defined by the user) and the process exits.

This guarantees that all data events with timestamps at or before the shutdown timestamp are fully processed before the node exits. At the same timestamp, `InputPortEvent` (priority 0) is always processed before `ShutdownEvent` (priority
1).

### 5. Error shutdown

If an unhandled exception occurs in a node's reaction, the node automatically calls `request_shutdown(0, status_code=1)` and exits with status code 1. The coordinator propagates the shutdown to all other nodes and exits with the non-zero
status code.

## Shutdown During `start()`

Nodes that run long-lived loops in `start()` (like `Timer`) exit when the `ShutdownEvent` has been processed (via `advance_time`) and the next `output_port(...)` call detects `shutdown_requested`.

The sequence is:

1. `drain_message_queue()` receives `ShutdownMessage`, pushes `ShutdownEvent` to event queue.
2. `advance_time()` processes events up to target, encounters `ShutdownEvent`, sets `shutdown_requested`, returns early.
3. The next `output_port(...)` call checks `shutdown_requested` and calls `sys.exit(0)`.
