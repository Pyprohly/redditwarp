
from __future__ import annotations
from typing import Optional, Any, Mapping, Iterator
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Token(Mapping[str, object]):
    access_token: str
    #_: KW_ONLY
    expires_in: Optional[int] = None
    d: Mapping[str, object] = field(repr=False, default_factory=dict)

    @staticmethod
    def from_dict(d: Mapping[str, Any]) -> Token:
        return Token(
            access_token=d['access_token'],
            expires_in=d.get('expires_in'),
            d=d,
        )

    def __contains__(self, item: object) -> bool:
        return item in self.d
    def __iter__(self) -> Iterator[str]:
        return iter(self.d)
    def __len__(self) -> int:
        return len(self.d)
    def __getitem__(self, key: str) -> object:
        return self.d[key]
