
from typing import T, Iterable, Sequence

from itertools import islice

def chunked(src: Iterable[T], size: int) -> Sequence[T]:
	it = iter(src)
	while True:
		chunk = tuple(islice(it, size))
		if not chunk:
			break
		yield chunk
