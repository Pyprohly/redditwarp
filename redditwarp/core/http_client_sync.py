
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Type, Any, Optional, Mapping, Dict
	from types import TracebackType
	from ..http.base_session_sync import BaseSession
	from .authorizer_sync import Authorizer
	from ..http.requestor_sync import Requestor
	from ..http.response import Response
	from ..http.payload import Payload

import sys
from time import sleep

from .. import auth
from ..http.transport import transport_reg
from ..auth.const import RESOURCE_BASE_URL
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
	def default_headers(self):
		return self._default_headers

	@property
	def user_agent(self):
		return self._default_headers['User-Agent']

	@user_agent.setter
	def user_agent(self, value):
		self._default_headers['User-Agent'] = value

	def __init__(self,
		requestor: Requestor,
		session: BaseSession,
		*,
		default_headers: Optional[Mapping[str, str]] = None,
		authorizer: Optional[Authorizer],
	) -> None:
		self.requestor = requestor
		self.session = session
		self._default_headers = {} if default_headers is None else default_headers
		self.authorizer = authorizer

		self.resource_base_url = RESOURCE_BASE_URL
		self.user_agent = self.USER_AGENT_STRING_HEAD

	def __enter__(self):
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
		path: str,
		*,
		params: Optional[Dict[str, str]] = None,
		payload: Optional[Payload] = None,
		data: Any = None,
		json: Any = None,
		headers: Optional[Dict[str, str]] = None,
		timeout: float = TIMEOUT,
		auxiliary: Optional[Mapping] = None,
	) -> Response:
		url = self.resource_base_url + path
		payload = make_payload(payload, data, json)
		params = {} if params is None else params
		headers = {} if headers is None else headers

		params.setdefault('raw_json', '1')
		params.setdefault('api_type', 'json')
		headers.update({**self.default_headers, **headers})

		r = Request(verb, url, params=params, payload=payload, headers=headers)

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
