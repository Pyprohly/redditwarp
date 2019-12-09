"""Transport adapter for Requests."""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .request import Request

import sys
from functools import partial
from http import HTTPStatus

import requests

from .. import exceptions
from .. import payload
from ..requestor import Requestor
from ..response import Response

TIMEOUT = 8

class Session(Requestor):
	def __init__(self) -> None:
		self.session = self._new_session()

		ua = 'RedditWarp/{0} Python/{1[0]}.{1[1]} requests/{2}'
		self.user_agent = ua.format('0.1', sys.version_info, requests.__version__)

	def _new_session(self) -> requests.Session:
		retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
		session = requests.Session()
		session.mount('https://', retry_adapter)
		self.session = session
		return session

	def request(self, request: Request, timeout: int = TIMEOUT) -> Response:
		r = request

		r.headers['User-Agent'] = self.user_agent

		request_partial = partial(
			self.session.request,
			method=r.verb,
			url=r.url,
			params=r.params,
			headers=r.headers,
			timeout=timeout,
		)
		d = r.data
		request_func = PAYLOAD_DISPATCH_TABLE[type(d)]
		resp = request_func(request_partial, d)
		response = Response(
			status=resp.status_code,
			headers=resp.headers,
			data=resp.content,
			response=resp,
			request=r,
		)
		import builtins; builtins.r = response
		return response

		#try:
		#except requests.exceptions.RequestException as exc:
		#	raise exceptions.TransportError(exc) from exc
		#else:


PAYLOAD_DISPATCH_TABLE = {
	type(None): lambda func, data: func(),
	payload.Raw: lambda func, data: func(data=data),
	payload.FormData: lambda func, data: func(data=data),
	payload.MultiPart: lambda func, data: func(files=data),
	payload.Text: lambda func, data: func(data=data),
	payload.JSON: lambda func, data: func(json=data),
}
