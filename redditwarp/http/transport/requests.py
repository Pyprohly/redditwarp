"""Transport adapter for Requests."""

from functools import partial
from http import HTTPStatus

import requests

from . import _abc
from .. import exceptions


TIMEOUT = 8

class Request(_abc.Request):
	"""Stores info about an outgoing request.
	"""

	def __init__(self, verb, url, *, headers=None):
		self.verb = verb
		self.url = url
		self.headers = headers

class Response(_abc.Response):
	# https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Response.body
	"""Requests response adapter."""

	@property
	def status(self):
		return self.response.status_code

	@property
	def headers(self):
		return self.response.headers

	@property
	def data(self):
		return self.response.content

	def __init__(self, response, request=None):
		""""
		Parameters
		----------
		response: :class:`requests.Response`
			The transport specific (Requests) response.
		request: :class:`Request`
			The request adaptor as context for this response.
		"""
		self.response = response
		self.request = request

class Requestor(_abc.Requestor):
	def __init__(self, session=None, user_agent=None):
		"""
		Parameters
		----------
		session: Optional[:class:`requests.Session`]
			A :class:`requests.Session` instance used to make HTTP requests.
			If not specified, a new session instance will be used.
		"""
		if session is None:
			session = requests.Session()
			retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
			session.mount('https://', retry_adapter)
		self.session = session

		self.user_agent = user_agent

	def __call__(self, request, timeout=TIMEOUT):
		r"""Make an HTTP request using requests.

		...

		Returns
		-------
		:class:`warp.http.auth.transport.Response`
			The HTTP response.

		Raises
		------
		:class:`warp.http.auth.exceptions.TransportError`
			If any exception occurred.
		"""
		r = request
		response = self.request(
			r.verb,
			r.url,
			params=r.params,
			data=r.data,
			json=r.json,
			headers=r.headers,
			files=r.files,
			timeout,
		)
		response.request = r
		return response

	def request(self, verb, url, *, params=None, data=None, json=None,
			headers=None, files=None, timeout=TIMEOUT):
		#try:
		#except requests.exceptions.RequestException as exc:
		#	raise exceptions.TransportError(exc) from exc
		#else:
		resp = self.session.request(verb, url, params=params, data=data, json=None,
				headers=headers, files=None, timeout=timeout)
		return Response(resp)


class AuthorizedSession(Requestor):
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

	#def __init__(self, credentials, requestor=None, token_requestor=None):
	def __init__(self, session=None, credentials=None):
		super().__init__(session)

		self.credentials = credentials

	def request(self, verb, url, data=None, headers=None, **kwargs):
		self.session.request(verb, url, )




		return
		"""Implementation of Requests' request."""

		if not self.credentials.valid():
			self.credentials.refresh(self._token_requestor)

		# !!!
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
		...

