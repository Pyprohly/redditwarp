
from __future__ import annotations
from typing import TypeVar, Iterable, Generic, Iterator

T = TypeVar('T')

class ObstinateChainIterator(Generic[T]):
	"""Like `itertools.chain.from_iterable()` but retains its state when
	an exception occurs during iteration.
	"""

	def __init__(self, iterable: Iterable[Iterable[T]]) -> None:
		self._iterator = iter(iterable)
		self._current_it: Iterable[T] = iter(())

	def __iter__(self) -> Iterator[T]:
		return self

	def __next__(self) -> T:
		while True:
			for element in self._current_it:
				return element
			self._current_it = next(self._iterator)
