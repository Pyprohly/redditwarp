
from typing import Type, TypeVar, Optional, Any, Mapping
from dataclasses import dataclass, field

__all__ = ('ResponseToken', 'Token')

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
	b: Mapping[str, Any]
		The bare json dictionary object.
	"""

	T = TypeVar('T', bound='ResponseToken')

	@classmethod
	def from_dict(cls: Type[T], b: Mapping[str, Any]) -> T:
		return cls(
			access_token=b['access_token'],
			token_type=b['token_type'],
			expires_in=b.get('expires_in'),
			refresh_token=b.get('refresh_token'),
			scope=b.get('scope'),
			b=b,
		)

	b: Mapping[str, Any] = field(default_factory=dict, repr=False)
