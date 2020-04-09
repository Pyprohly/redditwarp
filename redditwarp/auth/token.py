
from typing import Type, TypeVar, ClassVar, Optional, Any, Dict
from dataclasses import dataclass

__all__ = ('TokenResponse', 'Token')

T = TypeVar('T', bound='TokenResponse')

class TokenResponse:
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

	def __init__(self,
		access_token: str,
		token_type: str,
		expires_in: Optional[int] = None,
		refresh_token: Optional[str] = None,
		scope: Optional[str] = None,
		extra_params: Optional[Dict[str, Any]] = None,
	) -> None:
		self.access_token = access_token
		self.token_type = token_type
		self.expires_in = expires_in
		self.refresh_token = refresh_token
		self.scope = scope
		self.extra_params = {} if extra_params is None else extra_params

@dataclass(frozen=True)
class BearerToken:
	TOKEN_TYPE: ClassVar[str] = 'bearer'
	access_token: str
	token_type: str = TOKEN_TYPE
	expires_in: Optional[int] = None
	refresh_token: Optional[str] = None
	scope: Optional[str] = None

Token = BearerToken

def make_bearer_token(tr: TokenResponse) -> BearerToken:
	if tr.token_type.lower() != 'bearer':
		raise ValueError
	return BearerToken(
		access_token=tr.access_token,
		token_type=tr.token_type,
		refresh_token=tr.refresh_token,
		expires_in=tr.expires_in,
		scope=tr.scope,
	)
