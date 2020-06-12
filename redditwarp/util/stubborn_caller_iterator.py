
from __future__ import annotations
from typing import TypeVar, Generic, Iterable, Callable, Optional, Iterator

T = TypeVar('T')

class StubbornCallerIterator(Generic[T]):
	"""Call each callable in the given iterator and return its result.

	If a call raises an exception it will propagate normally. Doing
	`next(self)` will re-attempt the call until it returns a value.
	"""

	def __init__(self, iterable: Iterable[Callable[[], T]]) -> None:
		self._iterator = iter(iterable)
		self.current: Optional[Callable[[], T]] = None

	def __iter__(self) -> Iterator[T]:
		return self

	def __next__(self) -> T:
		if self.current is None:
			self.current = next(self._iterator)
		value = self.current()
		self.current = None
		return value
