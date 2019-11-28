
from dataclasses import dataclass

@dataclass(frozen=True)
class ClientCredentials:
	client_id: str
	client_secret: str
