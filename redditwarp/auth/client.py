
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..http.request import Request

from dataclasses import dataclass
from base64 import b64encode

@dataclass(frozen=True)
class ClientCredentials:
	client_id: str
	client_secret: str

def apply_basic_auth(client_credentials: ClientCredentials, request: Request) -> None:
	ci = client_credentials.client_id
	cs = client_credentials.client_secret
	auth_string = 'basic ' + b64encode(f'{ci}:{cs}'.encode()).decode()
	request.headers['Authorization'] = auth_string


from .client_sync import TokenClient as TokenClientSync, TokenClient  # noqa
from .client_async import TokenClient as TokenClientAsync  # noqa
