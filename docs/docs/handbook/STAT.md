---
sidebar_position: 2
---

# Safe To Advance To (STAT)

Apart from logical time, each node also maintains a Safe To Advance To(STAT) time value. STAT acts as a safeguard for the increase of logical time: the node's logical time is only allowed to advance to $t \lt \text{STAT}$. For
[eager reactions](eager), the bound is relaxed to $t \leq \text{STAT}$.

By default, STAT is set to `forever`, meaning that the logical time can grow whenever it wants. Consider a reaction triggered by two input ports A and B. If A receives a message with logical time $t_A$, the node will immediately advance to
$t_A$ since $t_A \lt \text{STAT}=\text{forever}$. Now the node receives another message with logical time $t_B \leq t_A$ and this will cause a problem since we now have to go backwards in time to process the new message.

This can be solved with STAT. If we know $t_B$ in advance and set STAT to $t_B$, since $t_B \leq t_A$, when we receive the message on port A, we know that we cannot process it yet since we have to wait for the message from $t_B$.

# Configuring STAT

A STAT can be set for each output port when sending a message. The API is

```python
self.output_port(<value>, STAT=<Time>)
```

Note that STAT is an interval instead of absolute time. The current logical time will be automatically added when sending STAT. One rule of thumb for setting STAT is to set it to the timestamp of the earliest next message (ENT, earliest
next timestamp). This will ensure that the downstream will not advance its logical time past the ENT, essentially waiting for this message before advancing to that logical time.
