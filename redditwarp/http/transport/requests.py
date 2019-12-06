"""Transport adapter for Requests."""

from functools import partial
from http import HTTPStatus

import requests

from . import _abc
from .. import exceptions
from .. import payload


TIMEOUT = 8

class Session(Requestor):
	def __init__(self):
		self.session = self._get_session()

		ua = 'RedditWarp/{0} Python/{1[0]}.{1[1]} request/{2}'
		self.user_agent = ua.format(__version__, sys.version_info, requests.__version__)

	def _get_session(self):
		retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
		session = requests.Session()
		session.mount('https://', retry_adapter)
		self.session = session
		return session

	def request(self, request, timeout=TIMEOUT):
		r = request

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
		return Response(resp, r)

		#try:
		#except requests.exceptions.RequestException as exc:
		#	raise exceptions.TransportError(exc) from exc
		#else:


PAYLOAD_DISPATCH_TABLE = {
	payload.Raw: lambda func, data: func(data=data),
	payload.FormData: lambda func, data: func(data=data),
	payload.MultiPart: lambda func, data: func(files=data),
	payload.Text: lambda func, data: func(data=data),
	payload.JSON: lambda func, data: func(json=data),
}
