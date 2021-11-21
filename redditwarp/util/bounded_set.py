
from __future__ import annotations
from typing import TypeVar, Iterator, Iterable

from collections.abc import MutableSet
from collections import deque

T = TypeVar('T')

class BoundedSet(MutableSet[T]):
    @property
    def maxlen(self) -> int:
        return self._maxlen

    def __init__(self, iterable: Iterable[T], maxlen: int) -> None:
        if maxlen < 0:
            raise ValueError('maxlen must be non-negative')
        self._maxlen = maxlen
        self._order: deque[T] = deque()
        self._stash: set[T] = set()
        for i in iterable:
            self.add(i)

    def __repr__(self) -> str:
        maxlen = self._maxlen
        return f'{self.__class__.__name__}({list(self)}, {maxlen=})'

    def __len__(self) -> int:
        return len(self._stash)

    def __contains__(self, item: object) -> bool:
        return item in self._stash

    def __iter__(self) -> Iterator[T]:
        return iter(self._stash)

    def add(self, value: T) -> None:
        if value in self._stash:
            return
        self._order.append(value)
        self._stash.add(value)
        if len(self) > self._maxlen:
            self._stash.remove(self._order.popleft())
        assert len(self._order) == len(self._stash)

    def discard(self, value: T) -> None:
        if value not in self._stash:
            return
        self._order.remove(value)
        self._stash.remove(value)

    def ordering(self) -> Iterator[T]:
        return iter(self._order)
