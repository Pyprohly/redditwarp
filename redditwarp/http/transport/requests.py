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

	def __init__(self, verb, url):
		self.verb = verb
		self.url = url

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

	def __init__(self, response):
		""""
		Parameters
		----------
		response: :class:`requests.Response`
			The Requests response.
		"""
		self.response = response
		self.request = None


class Requestor(_abc.Requestor):
	def __init__(self, session=None):
		"""
		Parameters
		----------
		session: Optional[:class:`requests.Session`]
			A :class:`requests.Session` instance used to make HTTP requests.
			If not specified, a new session instance will be used.
		"""
		if session is None:
			session = requests.Session()
		self.session = session

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

	def request(self, verb, url, *, data=None, headers=None, files=None, **kwargs):
		try:
			resp = self.session.request(
					verb, url, data=data, headers=headers,
					timeout=timeout, **kwargs)
		except requests.exceptions.RequestException as exc:
			raise exceptions.TransportError(exc) from exc
		else:
			return Response(resp)

class AuthorizedSession:
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

	def __init__(self,
			credentials,
			requestor=None,
			token_requestor=None):
		self.credentials = credentials

		def get_requestor():
			session = requests.Session()
			retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
			session.mount('https://', retry_adapter)
			return Requestor(session)

		self._requestor = requestor or get_requestor()
		self._token_requestor = token_requestor or get_requestor()

	def request(self, verb, url, data=None, headers=None, **kwargs):
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
			# the request, so make sure the response code is not 401.
			self.credentials.refresh(self._token_requestor)
			response = request()

		return response
