"""
Interfaces used by transport adapters to support various HTTP libraries
"""

import abc


class Request(abc.ABC):
	"""An ABC that stores info about an outgoing request.

	If applicable, calling the isntance produces a transport-specific Request instance.
	"""

	def __init__(self, url, method='GET', body=None, headers=None, **kwargs):
		r"""
		Parameters
		----------
		url: :class:`str`
			The URL to be requested.
		method: :class:`str`
			The HTTP method to use for the request. Defaults to 'GET'.
		body: Optional[:class:`bytes`]
			The payload/body in HTTP request.
		headers: Mapping[:class:`str`, :class:`str`]
			Request headers.
		\*\*kwargs
			Additional keyword arguments passed through to the transport
			specific requests method.
		"""
		self.url = url
		self.method = method
		self.body = body
		self.headers = headers
		self.kwargs = kwargs

	def __repr__(self):
		attrs = (
			('url', self.url),
			('method', self.method),
			('body', self.body),
			('headers', self.headers)
		)
		return '%s(%s%s)' % (
				type(self).__name__,
				', '.join('%s=%r' % t for t in attrs),
				', **%r' if self.kwargs else '')

	def __call__(self):
		"""Optional[T]: Returns a trasport specific request object,
		or ``None`` if not applicable for the transport being used.
		"""
		return None

class Requestor(abc.ABC):
	"""Interface for a callable that makes HTTP requests."""

	@abc.abstractmethod
	def __call__(self, url, method='GET', body=None, headers=None,
			timeout=None, **kwargs):
		r"""Make an HTTP request.

		Parameters
		----------
		url: str
			The URL to be requested.
		method: str
			The HTTP method to use for the request. Defaults to 'GET'.
		body: bytes
			The payload/body in HTTP request.
		headers: Mapping[str, str]
			Request headers.
		timeout: Optional[int]
			The number of seconds to wait for a response from the server.
			If not specified or if None, the requests default timeout will
			be used.
		\*\*kwargs
			Additional arguments passed on to the underlying
			transport's request method.

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

class Response(abc.ABC):
	"""HTTP Response data."""

	@abc.abstractproperty
	def status(self):
		"""int: The HTTP status code."""
		raise NotImplementedError

	@abc.abstractproperty
	def headers(self):
		"""Mapping[str, str]: The HTTP response headers."""
		raise NotImplementedError

	@abc.abstractproperty
	def data(self):
		"""bytes: The response body."""
		raise NotImplementedError
