
from __future__ import annotations
from typing import TypeVar, Iterable, Iterator, Sequence
from itertools import islice

T = TypeVar('T')

def chunked(src: Iterable[T], size: int) -> Iterator[Sequence[T]]:
    itr = iter(src)
    while chunk := tuple(islice(itr, size)):
        yield chunk

class ChunkingIterator(Iterator[Sequence[T]]):
    """Chunking iterator.

    The chunk size can be controlled during iteration using `.size`.
    """

    def __init__(self, src: Iterable[T], size: int) -> None:
        self._itr = iter(src)
        self.size: int = size
        ("")

    def __iter__(self) -> Iterator[Sequence[T]]:
        return self

    def __next__(self) -> Sequence[T]:
        if chunk := tuple(islice(self._itr, self.size)):
            return chunk
        raise StopIteration
