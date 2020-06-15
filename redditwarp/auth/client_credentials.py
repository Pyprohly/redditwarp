
from dataclasses import dataclass

__all__ = ('ClientCredentials',)

@dataclass(frozen=True)
class ClientCredentials:
    client_id: str
    client_secret: str
