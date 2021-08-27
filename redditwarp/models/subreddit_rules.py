
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, overload, Union

from datetime import datetime, timezone
from functools import cached_property

class Rule:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.kind: str = d['kind']
        self.description: str = d['description']
        self.description_html: str = d.get('description_html', '')
        self.short_name: str = d['short_name']
        self.violation_reason: str = d['violation_reason']
        self.created_ut = int(d['created_utc'])

    @cached_property
    def created_at(self) -> datetime:
        return datetime.fromtimestamp(self.created_ut, timezone.utc)


class SubredditRules(Sequence[Rule]):
    def __init__(self, d: Mapping[str, Any]):
        self.d = d
        self._rules = [Rule(o) for o in d['rules']]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._rules})'

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, item: object) -> bool:
        return item in self._rules

    def __iter__(self) -> Iterator[Rule]:
        return iter(self._rules)

    @overload
    def __getitem__(self, index: int) -> Rule: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[Rule]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[Rule, Sequence[Rule]]:
        return self._rules[index]
