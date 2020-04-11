
from typing import Type, TypeVar, Optional, Any, Mapping
from dataclasses import dataclass, field

__all__ = ('ResponseToken', 'Token')

T = TypeVar('T', bound='ResponseToken')


@dataclass(frozen=True)
class Token:
	access_token: str
	token_type: str = 'Bearer'
	expires_in: Optional[int] = None
	refresh_token: Optional[str] = None
	scope: Optional[str] = None

@dataclass(frozen=True)
class ResponseToken(Token):
	@classmethod
	def from_kwargs(cls: Type[T], **kwargs: Any) -> T:
		return cls(
			access_token=kwargs.pop('access_token'),
			token_type=kwargs.pop('token_type'),
			expires_in=kwargs.pop('expires_in', None),
			refresh_token=kwargs.pop('refresh_token', None),
			scope=kwargs.pop('scope', None),
			extra_params=kwargs,
		)

	extra_params: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DeviceIDResponseToken(ResponseToken):
	...
	device_id: str = ''
