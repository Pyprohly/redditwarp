
from typing import ClassVar, Optional, Dict, Any
from dataclasses import dataclass

class TokenResponse:
	token_type: ClassVar[str] = 'bearer'

	def __init__(self,
			access_token: str,
			expires_in: Optional[int] = None,
			refresh_token: Optional[str] = None,
			scope: Optional[str] = None,
			**kwargs: Any):
		self.access_token = access_token
		self.expires_in = expires_in
		self.refresh_token = refresh_token
		self.scope = scope
		self.extra_params = kwargs

	def _members(self):
		return {
			'access_token': self.access_token,
			'expires_in': self.expires_in,
			'refresh_token': self.refresh_token,
			'scope': self.scope,
			'extra_params': self.extra_params,
		}

	def __eq__(self, other):
		if other.__class__ is not self.__class__:
			return NotImplemented
		return self._members() == self._members()

@dataclass(frozen=True)
class Token:
	token_type: ClassVar[str] = 'bearer'
	access_token: str
	expires_in: Optional[int] = None
	refresh_token: Optional[str] = None
	scope: Optional[str] = None
