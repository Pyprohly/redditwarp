
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Type, Any, Optional, Dict
	from types import TracebackType
	from .tranport.base_session_sync import BaseSession
	from .requestor_sync import Requestor
	from .response import Response

import sys
from time import sleep

from .transport import requests as t_requests
from ..auth import RESOURCE_BASE_URL
from .request import Request
from .exceptions import HTTPResponseError, http_error_response_classes
from .. import __about__

_u = [
	(__about__.__title__, __about__.__version__),
	('Python', '.'.join(map(str, sys.version_info[:2]))),
	(t_requests.name, t_requests.version_string),
]
DEFAULT_USER_AGENT_STRING = ' '.join('/'.join(i) for i in _u)


class RedditHTTPClient:
	@property
	def user_agent(self) -> str:
		return self.session.headers['User-Agent']

	@user_agent.setter
	def user_agent(self, value) -> None:
		self.session.headers['User-Agent'] = value

	def __init__(self,
		requestor: Requestor,
		session: BaseSession,
	) -> None:
		self.requestor = requestor
		self.session = session
		self.authorizer = None
		self.resource_base_url = RESOURCE_BASE_URL
		self.user_agent = DEFAULT_USER_AGENT_STRING

	def __enter__(self) -> RedditHTTPClient:
		return self

	def __exit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		self.close()

	def request(self, verb: str, path: str, *, params: Optional[Dict[str, str]] = None,
			data: Any = None, headers: Optional[Dict[str, str]] = None, timeout: int = 8) -> Response:
		url = self.resource_base_url + path
		r = Request(verb, url, params=params, data=data, headers=headers)
		if 'raw_json' not in r.params:
			r.params['raw_json'] = '1'

		response = None
		status = -1
		for i in range(5):
			response = self.requestor.request(r, timeout)
			status = response.status

			if 200 <= status < 300:
				return response

			if status in (500, 502):
				sleep(2**i + 1)
				continue

			break

		clss = http_error_response_classes.get(status, HTTPResponseError)
		raise clss(response)

	def close(self) -> None:
		self.session.close()

HTTPClient = RedditHTTPClient
