
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Dict

from urllib.parse import urlencode

class AuthorizationCodeGrantRequestHelper:
	...

def authorization_url(
	url: str,
	response_type: str,
	client_id: str,
	redirect_uri: Optional[str],
	scope: Optional[str],
	state: Optional[str],
	extra_params: Optional[Dict[str, str]],
) -> str:
	extra_params = {} if extra_params is None else extra_params
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
