
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Dict

from urllib.parse import urlencode

from .provider import Provider


AUTHORIZATION_ENDPOINT = 'https://www.reddit.com/api/v1/authorize'
AUTHORIZATION_ENDPOINT_MOBILE = AUTHORIZATION_ENDPOINT + '.compact'
TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
RESOURCE_BASE_URL = 'https://oauth.reddit.com'

DEFAULT_PROVIDER = Provider(AUTHORIZATION_ENDPOINT, TOKEN_ENDPOINT, RESOURCE_BASE_URL)
MOBILE_PROVIDER = Provider(AUTHORIZATION_ENDPOINT_MOBILE, TOKEN_ENDPOINT, RESOURCE_BASE_URL)


class AuthorizationCodeGrantFlowRequestHelper:
	...

def authorization_url(
	url: str,
	response_type: str,
	client_id: str,
	redirect_uri: Optional[str],
	scope: Optional[str] = None,
	state: Optional[str] = None,
	extra_params: Optional[Dict[str, str]] = None,
) -> str:
	extra_params = extra_params or {}
	params = {
		'response_type': response_type,
		'client_id': client_id,
		'redirect_uri': redirect_uri,
		'scope': scope,
		'state': state,
		**extra_params,
	}
	params = {k: v for k, v in params.items() if v}
	return f'{url}?{urlencode(params)}'
