
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Callable, Iterable, Iterator

from .stubborn_caller_iterator import StubbornCallerIterator

T = TypeVar('T')

class CallChunkChainingIterator(Generic[T]):
	@property
	def current_call_chunk(self) -> Optional[Callable[[], Iterable[T]]]:
		return self._iterator.current

	def __init__(self, call_chunks: Iterable[Callable[[], Iterable[T]]]) -> None:
		self.call_chunks = call_chunks
		self._iterator = StubbornCallerIterator(call_chunks)
		self.current_chunk: Iterator[T] = iter(())

	def __iter__(self) -> Iterator[T]:
		return self

	def __next__(self) -> T:
		while True:
			for element in self.current_chunk:
				return element
			self.current_chunk = iter(next(self._iterator))
