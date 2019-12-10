
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict
if TYPE_CHECKING:
	from .response import Response

import sys
import requests

from .request import Request
from .transport.requests import Session

from .auth.provider import Provider
from .auth.credentials import ClientCredentials
from .authorizer import Authorized, Authorizer

AUTHORIZATION_ENDPOINT = 'https://www.reddit.com/api/v1/authorize'
TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
RESOURCE_BASE_URL = 'https://oauth.reddit.com'
DEFAULT_PROVIDER = Provider(AUTHORIZATION_ENDPOINT, TOKEN_ENDPOINT, RESOURCE_BASE_URL)

class HTTPClient:
	def __init__(self, session: Session, authorizer: Authorizer) -> None:
		# Ratelimited(Retryable(Session()))
		self.session = session
		self.authorizer = authorizer
		self.resource_base_url = RESOURCE_BASE_URL
		self.user_agent = 'RedditWarp/{0} Python/{1[0]}.{1[1]} requests/{2}' \
				.format('alpha', sys.version_info, requests.__version__)
		self.requestor = Authorized(session, authorizer)

	def request(self, verb: str, path: str, *, params: Optional[Dict[str, str]] = None,
			data: Any, headers: Dict[str, str] = None, timeout: int = 8) -> Response:
		url = self.resource_base_url + path
		r = Request(verb, url, params=params, data=data, headers=headers)
		r.headers['User-Agent'] = self.user_agent
		return self.requestor.request(r)
