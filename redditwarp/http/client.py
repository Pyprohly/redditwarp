
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict
if TYPE_CHECKING:
	from .response import Response

from .request import Request
from .transport.requests import Session

from .auth.provider import Provider
from .auth.credentials import ClientCredentials
from .auth.grant import ClientCredentialsGrant
from .auth.client import ClientCredentialsClient
from .authorizer import Authorized, Authorizer

class HTTPClient:
	AUTHORIZATION_URL = 'https://www.reddit.com/api/v1/authorize'
	TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
	RESOURCE_BASE_URL = 'https://oauth.reddit.com'
	NO_AUTH_RESOURCE_BASE_URL = 'https://www.reddit.com'

	def __init__(self) -> None:
		"""
		Attributes
		----------
		session: :class:`~.Requestor`
		"""
		#self.session = Ratelimited(Retryable(Session()))

		self.url_base = self.RESOURCE_BASE_URL

		self._token_requestor = Session()
		session = Session()
		provider = Provider(self.AUTHORIZATION_URL, self.TOKEN_ENDPOINT, self.RESOURCE_BASE_URL)
		client_credentials = ClientCredentials('GdfdxbF8ea73oQ', 'sOkVUjcTWNMZY11vWzlMAy4J7UE')
		grant = ClientCredentialsGrant()
		token_client = ClientCredentialsClient(self._token_requestor, provider, client_credentials, grant)
		authorized_session = Authorized(session, Authorizer(token_client))
		self.session = authorized_session

	def request(self, verb: str, path: str, *, params: Optional[Dict[str, str]] = None, data: Any, headers: Dict[str, str] = None) -> Response:
		url = self.url_base + path
		req = Request(verb, url, params=params, data=data, headers=headers)
		return self.session.request(req)
