
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, Union, overload

class Contributor:
    def __init__(self, d: Mapping[str, Any]):
        self.d: Mapping[str, Any] = d
        self.name: str = d['name']
        full_id36: str = d['id']
        _, _, id36 = full_id36.partition('_')
        self.id36: str = id36
        self.id: int = int(id36, 36)
        self.permissions: Sequence[str] = d['permissions']

class ContributorList(Sequence[Contributor]):
    def __init__(self,
            contributors: Sequence[Contributor],
            invitations: Sequence[Contributor]):
        self.contributors: Sequence[Contributor] = contributors
        self.invitations: Sequence[Contributor] = invitations

    def __len__(self) -> int:
        return len(self.contributors)

    def __contains__(self, item: object) -> bool:
        return item in self.contributors

    def __iter__(self) -> Iterator[Contributor]:
        return iter(self.contributors)

    @overload
    def __getitem__(self, index: int) -> Contributor: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Contributor]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Contributor, Sequence[Contributor]]:
        return self.contributors[index]
