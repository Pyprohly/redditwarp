"""
Interfaces used by transport adapters to support various HTTP libraries
"""

import abc

class Request(abc.ABC):
	"""An ABC that stores info about an outgoing request, and
	knows how to create transport-specific request objects.
	"""

	def __init__(self, verb, url, body=None, headers=None, **kwargs):
		r"""
		Parameters
		----------
		url: :class:`str`
			The URL to be requested.
		verb: :class:`str`
			The HTTP method to use for the request.
		body: Optional[:class:`bytes`]
			The payload/body in HTTP request.
		headers: Mapping[:class:`str`, :class:`str`]
			Request headers.
		\*\*kwargs
			Additional keyword arguments passed through to the transport
			specific requests method.
		"""
		self.verb = verb
		self.url = url
		self.body = body
		self.headers = headers
		self.kwargs = kwargs

	def __repr__(self):
		attrs = (
			('url', self.url),
			('verb', self.verb),
			('body', self.body),
			('headers', self.headers)
		)
		return '%s(%s%s)' % (
				type(self).__name__,
				', '.join('%s=%r' % t for t in attrs),
				f', **{self.kwargs}' if self.kwargs else '')

	@abc.abstractmethod
	def __call__(self):
		"""Optional[T]: Returns a trasport-specific request object,
		or ``None`` if not applicable for the transport being used.
		"""
		raise NotImplementedError

class Response(abc.ABC):
	"""An ABC that wraps a transport-specific HTTP response object."""

	def __init__(self, response):
		"""
		Parameters
		----------
		response: T
			The response object to wrap.
		"""
		self.response = response

	@abc.abstractproperty
	def status(self):
		""":class:`int`: The HTTP status code."""
		raise NotImplementedError

	@abc.abstractproperty
	def headers(self):
		"""Mapping[:class:`str`, :class:`str`]: The HTTP response headers."""
		raise NotImplementedError

	@abc.abstractproperty
	def data(self):
		""":class:`bytes`: The response body."""
		raise NotImplementedError


class Requestor(abc.ABC):
	"""Encapsulate the thing that is the requestor. This is often known
	as the 'Session' object.
	"""

	###!!- """A wrapper for a callable that makes HTTP requests."""


	@abc.abstractmethod
	def request(self, verb, url, timeout=None):
		r"""Make an HTTP request.

		Parameters
		----------
		...

		Returns
		-------
		:class:`Response`
			The HTTP response.

		Raises
		------
		:class:`warp.http.auth.exceptions.TransportError`
			If any exception occurred.
		"""
		raise NotImplementedError



	##-
	'''
	@abc.abstractmethod
	def __call__(self, request, timeout=None):
		r"""Make an HTTP request.

		Parameters
		----------
		request: :class:`Request`
			The URL to be requested.
		timeout: Optional[:class:`int`]
			The number of seconds to wait for a response from the server.
			If ``None``, the transport default timeout will be used.

		Returns
		-------
		:class:`Response`
			The HTTP response.

		Raises
		------
		:class:`warp.http.auth.exceptions.TransportError`
			If any exception occurred.
		"""
		raise NotImplementedError
	'''
