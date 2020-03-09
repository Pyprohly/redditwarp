
from __future__ import annotations
from typing import T, Iterable

class TheStubbornCallerIterator:
	"""For each callable in the given iterator, call it and return its result.

	If a callable raises an exception, it will propagate normally. The next
	`next(self)` call will re-attempt the callable until it returns a value.
	"""

	def __init__(self, iterable: Iterable[Callable[[], T]]) -> None:
		self._iterator = iter(iterable)
		self.current_callable = None

	def __iter__(self):
		return self

	def __next__(self) -> T:
		if self.current_callable is None:
			self.current_callable = next(self._iterator)
		value = self.current_callable()
		self.current_callable = None
		return value
