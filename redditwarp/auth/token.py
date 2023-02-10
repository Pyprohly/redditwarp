
from __future__ import annotations
from typing import TypeVar, Optional, Any, Mapping, Iterator
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Token(Mapping[str, object]):
    """OAuth2 token information."""

    access_token: str
    #_: KW_ONLY
    token_type: str = 'Bearer'
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    d: Mapping[str, object] = field(repr=False, default_factory=dict)

    _TSelf = TypeVar('_TSelf', bound='Token')

    @classmethod
    def from_dict(cls: type[_TSelf], d: Mapping[str, Any]) -> _TSelf:
        """Create an instance from OAuth2 token data."""
        return cls(
            access_token=d['access_token'],
            token_type=d['token_type'],
            expires_in=d.get('expires_in'),
            refresh_token=d.get('refresh_token'),
            scope=d.get('scope'),
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
