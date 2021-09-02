
from __future__ import annotations
from typing import Sequence, TypeVar, overload, Iterator, Union, Generic

from .submission_draft import Draft

class BaseDraftList(Sequence[Draft]):
    def __init__(self, drafts: Sequence[Draft]):
        self.drafts = drafts

    def __len__(self) -> int:
        return len(self.drafts)

    def __contains__(self, item: object) -> bool:
        return item in self.drafts

    def __iter__(self) -> Iterator[Draft]:
        return iter(self.drafts)

    @overload
    def __getitem__(self, index: int) -> Draft: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Draft]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Draft, Sequence[Draft]]:
        return self.drafts[index]

T = TypeVar('T')

class GenericBaseDraftList(BaseDraftList, Generic[T]):
    def __init__(self,
            drafts: Sequence[Draft],
            subreddits: Sequence[T]):
        super().__init__(drafts)
        self.subreddits = subreddits
