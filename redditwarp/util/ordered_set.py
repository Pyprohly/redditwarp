
from __future__ import annotations
from typing import TypeVar, Iterator, Iterable

from collections.abc import MutableSet
from itertools import islice

T = TypeVar('T')

class OrderedSet(MutableSet[T]):
    def __init__(self, it: Iterable[T]) -> None:
        store: dict[T, None] = {}
        self._store = store
        for i in it:
            store[i] = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({list(self)})'

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, item: object) -> bool:
        return item in self._store

    def __iter__(self) -> Iterator[T]:
        return iter(self._store)

    def add(self, value: T) -> None:
        self._store[value] = None

    def discard(self, value: T) -> None:
        self._store.pop(value, None)


class BoundedSet(OrderedSet[T]):
    @property
    def capacity(self) -> int:
        return self._capacity

    def __init__(self, it: Iterable[T], capacity: int) -> None:
        if capacity < 0:
            raise ValueError('capacity must be non-negative')
        self._capacity = capacity
        super().__init__(it)

        store = self._store
        keys = list(islice(store, max(len(store) - capacity, 0)))
        for key in keys:
            del store[key]

    def __repr__(self) -> str:
        capacity = self._capacity
        return f'{self.__class__.__name__}({list(self)}, {capacity=})'

    # https://mobile.twitter.com/raymondh/status/1150079085114093568
    def _from_iterable(self, it: Iterable[T]) -> BoundedSet[T]:
        return type(self)(it, capacity=self._capacity)

    def add(self, value: T) -> None:
        super().add(value)
        if len(self) > self._capacity:
            del self._store[next(iter(self._store))]
