---
sidebar_position: 3
---

# Eager Reactions

In feedback loops (e.g., `A → B → A`), a normal `yield` can deadlock: the yield waits for STAT to advance strictly past the target time, but STAT depends on a message that can only be sent after the yield returns. This is a **causality
loop**.

`@reaction([...], eager=True)` resolves this by relaxing the STAT bound from $t \lt \text{STAT}$ to $t \leq \text{STAT}$. This allows the reaction to resume when its yield target equals STAT exactly, breaking the circular dependency.

```python
@reaction([action_in], eager=True)
def on_action(self):
    frame = self.env.step(self.action_in)
    yield self.dt                          # resumes when STAT >= dt (inclusive)
    self.observation(frame, STAT=self.dt)
```

See [Simulation](../tutorial/simulation) for a full example.
