"""Reaction queue for scheduling and executing triggered reactions."""

from collections import deque
from typing import Callable, Optional, Tuple

from rosia.time import Time


class ReactionQueue:
    """FIFO queue of pending reactions ready to execute.

    When an InputPortEvent is processed, its triggered reactions are
    enqueued here.  ``advance_logical_time`` always drains this queue
    before popping the next event, guaranteeing that all reactions at
    timestamp T complete before any event at T' > T is processed.
    This keeps ``logical_time`` monotonically non-decreasing.
    """

    def __init__(self) -> None:
        self._queue: deque[Tuple[Callable, Time]] = deque()

    def enqueue(self, function: Callable, timestamp: Time) -> None:
        self._queue.append((function, timestamp))

    def dequeue(self) -> Optional[Tuple[Callable, Time]]:
        if self._queue:
            return self._queue.popleft()
        return None

    def has_pending(self) -> bool:
        return bool(self._queue)
