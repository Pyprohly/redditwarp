
from dataclasses import dataclass

@dataclass
class Provider:
	auth_endpoint: str
	token_endpoint: str
	resource_base_url: str
