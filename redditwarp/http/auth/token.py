
from typing import ClassVar, Optional, Dict
from dataclasses import dataclass

@dataclass
class _BaseBearerTokenDataclass:
	token_type: ClassVar[str] = 'bearer'
	access_token: str
	refresh_token: Optional[str]
	expires_in: int

@dataclass
class TokenResponse(_BaseBearerTokenDataclass):
	scope: Optional[str]
	state: Optional[str]
	extra_params: Dict[str, str]

	@classmethod
	def from_json_dict(cls, json_dict):
		return cls(
			access_token=json_dict.pop('access_token'),
			refresh_token=json_dict.pop('refresh_token', None),
			expires_in=json_dict.pop('expires_in'),
			scope=json_dict.pop('scope', None),
			state=json_dict.pop('state', None),
			extra_params=json_dict,
		)

class Token(_BaseBearerTokenDataclass):
	pass
