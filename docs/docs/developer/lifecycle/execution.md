---
sidebar_position: 4
---

# Node Execution

After startup completes, each node enters its main event loop. The loop processes incoming messages, computes how far it can safely advance in logical time, and fires reactions when it is safe to do so.

## Event Loop

The event loop (`event_loop()`) repeats these steps:

1. **Drain messages**: Pull all pending messages from the transport (non-blocking). Each message updates the event queue, reaction queue, or port STAT values.
2. **Update STAT**: Recompute the node's Safe To Advance To (STAT) time from input port STATs and the shutdown barrier.
3. **Check for work**: The node has work if:
   - There is an event in the event queue with timestamp $t \lt \text{STAT}$, or
   - There is a reaction in the reaction queue with timestamp $t \leq \text{STAT}$.
4. **Act**:
   - If there is work, call `advance_to_STAT()` to process events and reactions.
   - If there is no work and all upstream ports have finished, initiate natural shutdown.
   - Otherwise, block until a new message arrives on the transport.

```
while True:
    drain_message_queue()
    update_STAT()
    if has_work:
        advance_to_STAT()
    elif check_natural_shutdown():
        return
    else:
        wait_for_message()
```

## Message Draining

`drain_message_queue()` pulls all available messages from the transport without blocking. Each message type is handled differently:

| Message type                        | Effect                                                                                                                                             |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Message` (timestamped)             | Pushed to the event queue at the message's logical timestamp. Updates the upstream output port's STAT.                                             |
| `Message` (physical, no timestamp)  | Sets the input port value immediately and enqueues a reaction at the current logical time.                                                         |
| `NoMoreMessage`                     | Decrements the input port's `active_upstream_count`. Sets the upstream port's STAT to `forever`.                                                   |
| `ShutdownMessage`                   | Sets the shutdown barrier and pushes a `ShutdownEvent` at the shutdown timestamp. If the timestamp is already in the past, shuts down immediately. |
| `ApplicationRequestShutdownMessage` | Part of shutdown negotiation. The node responds with the later of its current logical time and the requested time.                                 |

When a `Message` carries a STAT value, the STAT of the corresponding upstream output port is updated (monotonically increasing), and the input port recomputes its own STAT as the minimum of all its upstream ports' STATs.

## STAT Computation

`update_STAT()` sets the node's STAT to:

$$
\text{STAT} = \min\bigl(\min_{\text{input ports}} \text{port.safe\_to\_advance\_to},\;\text{shutdown\_time\_barrier}\bigr)
$$

This ensures a node never advances its logical time beyond what its upstream connections guarantee is safe, and never past a pending shutdown.

## Advancing to STAT

`advance_to_STAT()` processes all events and reactions whose timestamps fall within the STAT boundary. It loops through the following until no more work can be done:

1. **Drain and update**: Re-drain messages and recompute STAT (new messages may have arrived during processing).
2. **Pick the next timestamp**: The earliest timestamp across both the event queue and reaction queue.
3. **Boundary check**: If the next timestamp exceeds STAT, return and wait. If it equals STAT and no eager reaction is pending, also return and wait.
4. **Advance logical time** to the chosen timestamp.
5. **Execute pending reactions** at this timestamp.
6. **Process events** at this timestamp:
   - `InputPortEvent`: Sets port values from the event, collects the associated trigger functions, and enqueues a `Reaction` for each.
   - `ShutdownEvent`: Enqueues a shutdown reaction.
7. **Execute newly enqueued reactions** from step 6.

All reactions at timestamp $t$ complete before any event at $t' > t$ is processed, preserving causal order.

## Reaction Execution

`execute_reactions()` dequeues and runs all reactions at a given timestamp:

- **Regular reactions**: The reaction's function is called on the node instance. If the function is a generator (uses `yield`), the yielded time delta determines when the reaction resumes — it is re-enqueued at `timestamp + delta`.
- **Shutdown reactions**: When a shutdown reaction is dequeued, the node shuts down immediately.

Reactions that raise `TerminateReactionException` are silently terminated without propagating the error.

## Physical Messages

Physical messages (messages with no timestamp) bypass the event queue entirely. When a physical message arrives during `drain_message_queue()`, the input port value is set immediately and a reaction is enqueued at the node's current logical
time. This is used for out-of-band communication that does not participate in logical time ordering.
