
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Type, Any, Optional, Mapping, MutableMapping
	from types import TracebackType
	from ..http.base_session_sync import BaseSession
	from .authorizer_sync import Authorizer, Authorized
	from ..http.requestor_sync import Requestor
	from ..http.response import Response
	from ..http.payload import Payload

import sys
from time import sleep

from .. import auth
from ..http.transport import transport_reg
from ..http.request import Request
from .. import __about__
from ..http.payload import make_payload
from .exceptions import raise_for_auth_response_exception

transport_info = transport_reg['requests']

class RedditHTTPClient:
	TIMEOUT = 8
	USER_AGENT_STRING_HEAD = (
		f"{__about__.__title__}/{__about__.__version__} "
		f"Python/{'{0[0]}.{0[1]}'.format(sys.version_info)} "
		f"{transport_info.name}/{transport_info.version_string}"
	)

	@property
	def default_headers(self) -> MutableMapping[str, str]:
		return self._default_headers

	@property
	def user_agent(self) -> str:
		return self._default_headers['User-Agent']

	@user_agent.setter
	def user_agent(self, value: str) -> None:
		self._default_headers['User-Agent'] = value

	@property
	def authorizer(self) -> Optional[Authorizer]:
		if self.authorized_requestor is None:
			return None
		return self.authorized_requestor.authorizer

	@authorizer.setter
	def authorizer(self, value: Authorizer) -> None:
		if self.authorized_requestor is None:
			raise RuntimeError('The client is not configured in a way that knows how update this field.')
		self.authorized_requestor.authorizer = value

	def __init__(self,
		session: BaseSession,
		requestor: Optional[Requestor],
		*,
		default_headers: Optional[MutableMapping[str, str]] = None,
		authorized_requestor: Optional[Authorized],
	) -> None:
		self.session = session
		self.requestor = session if requestor is None else requestor
		self._default_headers = {} if default_headers is None else default_headers
		self.authorized_requestor = authorized_requestor
		self.user_agent = self.USER_AGENT_STRING_HEAD

	def __enter__(self) -> RedditHTTPClient:
		return self

	def __exit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		self.close()
		return None

	def request(self,
		verb: str,
		uri: str,
		*,
		params: Optional[MutableMapping[str, str]] = None,
		payload: Optional[Payload] = None,
		data: Any = None,
		json: Any = None,
		headers: Optional[MutableMapping[str, str]] = None,
		timeout: float = TIMEOUT,
		auxiliary: Optional[Mapping] = None,
	) -> Response:
		payload = make_payload(payload, data, json)
		params = {} if params is None else params
		headers = {} if headers is None else headers

		params.setdefault('raw_json', '1')
		params.setdefault('api_type', 'json')
		headers.update({**self.default_headers, **headers})

		r = Request(verb, uri, params=params, payload=payload, headers=headers)

		for i in range(5):
			try:
				resp = self.requestor.request(r, timeout=timeout, auxiliary=auxiliary)

			except auth.exceptions.ResponseException as e:
				raise_for_auth_response_exception(e)
				raise

			if resp.status in (500, 502):
				sleep(i**2)
				continue
			break

		return resp

	def close(self) -> None:
		self.session.close()

HTTPClient = RedditHTTPClient
