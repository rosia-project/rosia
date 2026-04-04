"""Generator utilities for driving user generators that yield Time deltas."""

import inspect
from typing import Any

from rosia.time import Time
from rosia.coordinate.Events import EventQueue


def is_generator(result: Any) -> bool:
    return inspect.isgenerator(result)


def resume_generator(logical_time: Time, event_queue: EventQueue, gen: Any) -> bool:
    """Resume a generator. If it yields a Time, push a YieldCompleteEvent.
    Returns True if the generator is still active, False if it finished."""
    try:
        delta = next(gen)
        if not isinstance(delta, Time):
            raise TypeError(
                f"Expected yield of Time, got {type(delta).__name__}: {delta}"
            )
        target_time = logical_time + delta
        event_queue.push_yield_complete_event(target_time, gen)
        return True
    except StopIteration:
        return False
