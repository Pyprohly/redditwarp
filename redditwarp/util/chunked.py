
from typing import TypeVar, Iterable, Iterator, Sequence
from itertools import islice

T = TypeVar('T')

def chunked(src: Iterable[T], size: int) -> Iterator[Sequence[T]]:
    itr = iter(src)
    while True:
        chunk = tuple(islice(itr, size))
        if not chunk:
            break
        yield chunk
