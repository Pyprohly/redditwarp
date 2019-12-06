
from typing import ClassVar, Optional, Dict
from dataclasses import dataclass

@dataclass
class TokenResponse:
	token_type: ClassVar[str] = 'bearer'
	access_token: str
	refresh_token: Optional[str]
	expires_in: int
	scope: Optional[str]
	state: Optional[str]
	extra_params: Dict[str, str]

@dataclass
class Token:
	token_type: ClassVar[str] = 'bearer'
	access_token: str
	refresh_token: Optional[str]
	expires_in: int
