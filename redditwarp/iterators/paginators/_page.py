
from typing import TypeVar, Sequence, Iterator, List, Optional, overload

T = TypeVar('T')

class Page(Sequence[T]):
	def __init__(self) -> None:
		self.cursor: Optional[str] = None
		self._results: Sequence[T]

	def __repr__(self) -> str:
		return f'{self.__class__.__name__}({self._results})'

	def __len__(self) -> int:
		return len(self._results)

	def __contains__(self, item: object) -> bool:
		return item in self._results

	def __iter__(self) -> Iterator[T]:
		return iter(self._results)

	@overload
	def __getitem__(self, index: int) -> T: pass
	@overload
	def __getitem__(self, index: slice) -> List[T]: pass
	def __getitem__(self, index):
		return self._results[index]
