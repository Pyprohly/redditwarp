"""Transport adapter for Requests."""

from functools import partial
from http import HTTPStatus

import requests

from . import _abc
from .. import exceptions
from .. import payload


TIMEOUT = 8


class RequestorDecorator(Requestor):
	def __init__(self, requestor):
		self.requestor = requestor

	def request(self, request, **kwargs):
		return self.requestor.request(request, **kwargs)

class Authorized(RequestorDecorator):
	"""A Requests Session wrapper class that holds credentials.

	This class is used to perform requests to API endpoints that require
	authorization. The :meth:`request` method handles adding authorization
	headers to the request and refreshing credentials when needed.

	Parameters
	----------
	credentials: :class:`warp.http.auth.credentials.Credentials`
		The credentials to apply to requests.
	requestor: Optional[:class:`~.Requestor`]
		The requestor used when making API requests.
	token_requestor: Optional[:class:`~.Requestor`]
		The requestor used for refreshing credentials.
	"""

	def __init__(self, requestor, token_client):
		super().__init__(requestor)
		self.token_client = token_client

	def request(self, request, timeout=TIMEOUT):
		self.prepare_request(request)
		resp = self.requestor.request(request)
		return resp


		return
		if not self.credentials.valid():
			self.credentials.refresh(self._token_requestor)

		self.credentials.prepare_requestor(self._requestor)
		request = partial(self.credentials.prepare_requestor(self._requestor),
				url=url, verb=verb, data=data, headers=headers, **kwargs)

		response = request()
		if response.status == 401:
			'''
			log.info(
				'Refreshing credentials due to a %s response. Attempt %s/%s.',
				response.status_code, _credential_refresh_attempt + 1,
				self._max_refresh_attempts)
			'''
			# Even though we check the credentials before making the request,
			# the token could have expired in the time between the check and
			# the request. Check that the response code is not 401.
			self.credentials.refresh(self._token_requestor)
			response = request()

		return response

	def prepare_request(self, request):
		


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
