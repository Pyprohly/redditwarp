
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Mapping
	from .client_credentials import ClientCredentials
	from ..http.request import Request

from base64 import b64encode
from urllib.parse import urlencode

__all__ = (
	'authorization_url',
	'apply_basic_auth',
)

def authorization_url(
	url: str,
	response_type: str,
	client_id: str,
	redirect_uri: Optional[str],
	scope: Optional[str] = None,
	state: Optional[str] = None,
	extra_params: Optional[Mapping[str, str]] = None,
) -> str:
	params = {
		'response_type': response_type,
		'client_id': client_id,
		'redirect_uri': redirect_uri,
		'scope': scope,
		'state': state,
		**(extra_params or {}),
	}
	params = {k: v for k, v in params.items() if v}
	return f'{url}?{urlencode(params)}'

def apply_basic_auth(request: Request, client_credentials: ClientCredentials) -> None:
	ci = client_credentials.client_id
	cs = client_credentials.client_secret
	hv = 'basic ' + b64encode(f'{ci}:{cs}'.encode()).decode()
	request.headers['Authorization'] = hv
