
from __future__ import annotations
from typing import TypeVar, Iterable, Iterator, Sequence, Generic
from itertools import islice

T = TypeVar('T')

def chunked(src: Iterable[T], size: int) -> Iterator[Sequence[T]]:
    itr = iter(src)
    while True:
        chunk = tuple(islice(itr, size))
        if not chunk:
            break
        yield chunk


class ChunkingIterator(Generic[T]):
    """Control chunk size during iteration."""

    def __init__(self, src: Iterable[T], size: int) -> None:
        self._itr = iter(src)
        self.size = size

    def __iter__(self) -> Iterator[Sequence[T]]:
        return self

    def __next__(self) -> Sequence[T]:
        chunk = tuple(islice(self._itr, self.size))
        if not chunk:
            raise StopIteration
        return chunk
