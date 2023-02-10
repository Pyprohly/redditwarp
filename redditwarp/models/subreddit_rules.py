
from __future__ import annotations
from typing import Mapping, Any, Sequence, Iterator, overload, Union

from enum import Enum, auto

class RuleScope(Enum):
    ALL = auto()
    SUBMISSION = auto()
    COMMENT = auto()

class Rule:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.scope: RuleScope = {
            'all': RuleScope.ALL,
            'link': RuleScope.SUBMISSION,
            'comment': RuleScope.COMMENT,
        }[d['kind']]
        ("""
            Content this rule applies to.

            Enum: :class:`.RuleScope`.
            """)
        self.short_name: str = d['short_name']
        ("""
            Short description.

            Up to 100 characters.
            """)
        self.description: str = d['description']
        ("""
            Description.

            Up to 500 characters.
            """)
        self.description_html: str = d.get('description_html', '')
        ("""
            Same as :attr:`description` but HTML formatted.
            """)
        self.violation_reason: str = d['violation_reason']
        ("""
            Violation reason text.

            Up to 100 characters.

            Value matches `short_name` if left empty in the UI. It's unfortunately not possible
            to tell if this field is empty through the API.
            """)
        self.created_ut: int = int(d['created_utc'])
        ("""
            Unix timestamp of when the rule was created.
            """)


class SubredditRules(Sequence[Rule]):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self._rules = [Rule(o) for o in d['rules']]

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
