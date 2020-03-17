
from typing import ClassVar, Optional, Any
from dataclasses import dataclass

__all__ = ('TokenResponse', 'Token')

class TokenResponse:
	def __init__(self,
			access_token: str,
			token_type: str,
			expires_in: Optional[int] = None,
			refresh_token: Optional[str] = None,
			scope: Optional[str] = None,
			**extra_params: Any):
		self.access_token = access_token
		self.token_type = token_type
		self.expires_in = expires_in
		self.refresh_token = refresh_token
		self.scope = scope
		self.extra_params = extra_params

@dataclass(frozen=True)
class BearerToken:
	TOKEN_TYPE: ClassVar[str] = 'bearer'
	access_token: str
	expires_in: Optional[int] = None
	refresh_token: Optional[str] = None
	scope: Optional[str] = None

Token = BearerToken
