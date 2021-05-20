
from typing import Type, TypeVar, Optional, Any, Mapping
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Token:
    access_token: str
    token_type: str = 'Bearer'
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

@dataclass(frozen=True)
class ResponseToken(Token):
    """
    Attributes
    ----------
    d: Mapping[str, Any]
        The JSON object dictionary.
    """

    d: Mapping[str, Any] = field(repr=False, default_factory=dict)

    T = TypeVar('T', bound='ResponseToken')

    @classmethod
    def from_dict(cls: Type[T], d: Mapping[str, Any]) -> T:
        return cls(
            access_token=d['access_token'],
            token_type=d['token_type'],
            expires_in=d.get('expires_in'),
            refresh_token=d.get('refresh_token'),
            scope=d.get('scope'),
            d=d,
        )
