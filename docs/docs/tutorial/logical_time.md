---
sidebar_position: 6
---

# Logical Time

In Rosia, each node has it's own _logical time_. It can be the physical time of your computer's clock, it can be time in the simulation you're running, or it could be any ordering of messages of events that you define it to be.

The logical time can be monotonoically increased in the following ways:

- Before executing `start()`, each node's logical time is set to `Time(0)`.
- Inside `start()` and reactions marked with `@reaction()` annotator, you can manually advance time by interval `<Time>` with `yield <Time>`. For example, `yield 1*s` will advance logical time by 1 second.
- When a reaction is triggered by reacting to input ports defined in `@reaction(<ports>)`, the node will advance logical time to the logical time associated with the message received at the input port.

The point of having logical time is to give an order to all messages and reactions. Messages with the same logical time are considered simultaneous. As shown in example [Synchronization](tutorial/synchronization), if multiple input ports
have the same logical time, they will be synchronized to only trigger the reaction once.

# Safe To Advance To (STAT)

Apart from logical time, each node also maintains a Safe To Advance To(STAT) Time value. STAT acts as a safeguard for the increase of logical time: the node's logical time is only allowed to advance to $t$ < STAT.

By default, STAT is set to `forever`, meaning that the logical time can grow whenever it wants. Consider a reaction with two input ports A and B. If A receives a message with logical time $t_A$, the node will immediately advance to $t_A$
since $t_A < \text{STAT}=\text{forever}$. Now the node receives another message with logical time $t_B <= t_A$ and this will cause a problem since we now have to go backwards in time to process the new message.

This can be solved with decreasing STAT. If we know $t_B$ in advance and set STAT to $t_B$, since $t_B <= t_A$, when we receive the message on port A, we know that we cannot process it yet since we have to wait for the message from $t_B$.

The calculation of STAT get complicated when there are multiple nodes and ports.

# Loops

How to send message with timestamp in the future?

Send messages without actually increasing node's logical time. after delay. No!

Yield to t does not process input event at t yet. It just process all input events < t. Then finish yield. Though logical time is at time t, the input events are not processed.

If another reaction yields at the same timestamp, just put it after the previous yield.

# Structures

- logical_time
- STAT

- event queue: input messages at each timestamp
- reaction_queue: ordered by timestamp, then by yield order

# Event loop

- drain message queue and put on event queue, update stat while doing so
- advance time
  - execute reaction queue at the current time stamp # This should only contain yielded reactions
  - put event queue onto reaction queue
  - loop
- loop

# Yield Procedure

- put generator onto reaction queue at the yield timestamp
- go into event loop
