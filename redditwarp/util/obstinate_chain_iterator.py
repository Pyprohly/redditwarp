
from __future__ import annotations
from typing import T, Iterable

class ObstinateChainIterator:
	"""Like `itertools.chain.from_iterable()` but retains its state when
	an exception occurs during iteration.
	"""

	def __init__(self, iterable: Iterable[Iterable[T]]) -> None:
		self._iterator = iter(iterable)
		self._current_it = iter(())

	def __iter__(self):
		return self

	def __next__(self) -> T:
		while True:
			for element in self._current_it:
				return element
			self._current_it = next(self._iterator)
