
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
	access_token: str
	refresh_token: str
	expires_in: int
