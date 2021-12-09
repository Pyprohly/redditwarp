
from __future__ import annotations
from typing import Callable

from collections.abc import Sized
import time
from heapq import heappush, heappop

class Entry:
    def __init__(self, when: float, callback: Callable[[], None]) -> None:
        self.when: float = when
        self.callback: Callable[[], None] = callback
        self.scheduled: bool = True
        self.cancelled: bool = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.when == other.when
        return NotImplemented
    def __lt__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.when < other.when
        return NotImplemented
    def __le__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.when <= other.when
        return NotImplemented
    def __gt__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.when > other.when
        return NotImplemented
    def __ge__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.when >= other.when
        return NotImplemented

class Handle:
    def __init__(self, entry: Entry) -> None:
        self._entry = entry

    def get_when(self) -> float:
        return self._entry.when

    def get_cancelled(self) -> bool:
        return self._entry.cancelled

    def get_scheduled(self) -> bool:
        return self._entry.scheduled

    def cancel(self) -> None:
        self._entry.cancelled = True


class Scheduler(Sized):
    def __init__(self,
        *,
        time_func: Callable[[], float] = time.monotonic,
        delay_func: Callable[[float], None] = time.sleep,
    ) -> None:
        self.time_func: Callable[[], float] = time_func
        self.delay_func: Callable[[float], None] = delay_func
        self._pq: list[Entry] = []

    def __len__(self) -> int:
        return len(self._pq)

    def empty(self) -> bool:
        return not self._pq

    def time(self) -> float:
        return self.time_func()

    def call_at(self, when: float, callback: Callable[[], None]) -> Handle:
        entry = Entry(when, callback)
        heappush(self._pq, entry)
        return Handle(entry)

    def call_later(self, delay: float, callback: Callable[[], None]) -> Handle:
        return self.call_at(self.time() + delay, callback)

    def call_soon(self, callback: Callable[[], None]) -> Handle:
        return self.call_later(0, callback)

    def jog(self) -> float:
        pq = self._pq
        while pq:
            entry = pq[0]
            if entry.cancelled:
                heappop(pq)
                entry.scheduled = False
                continue

            curr_time = self.time_func()
            if entry.when > curr_time:
                return entry.when - curr_time

            heappop(pq)
            entry.scheduled = False
            entry.callback()
        return -1

    def run(self) -> None:
        while True:
            slack_time = self.jog()
            if slack_time < 0:
                break
            self.delay_func(slack_time)
