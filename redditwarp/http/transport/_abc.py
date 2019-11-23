"""
Interfaces used by transport adapters to support various HTTP libraries
"""

import abc

class Request(abc.ABC):
	"""An ABC that stores info about an outgoing request, and
	knows how to create transport-specific request objects.
	"""

	def __init__(self, verb, url, data=None, headers=None, **kwargs):
		r"""
		Parameters
		----------
		url: str
			The URL to be requested.
		verb: str
			The HTTP method to use for the request.
		data: Optional[bytes]
			The payload/body in HTTP request.
		headers: Mapping[str, str]
			Request headers.
		\*\*kwargs
			Additional keyword arguments are passed to the transport
			specific request method.
		"""
		self.verb = verb
		self.url = url
		self.data = data
		self.headers = headers
		self.kwargs = kwargs

	def __repr__(self):
		attrs = (
			('url', self.url),
			('verb', self.verb),
			('data', self.data),
			('headers', self.headers)
		)
		return '%s(%s%s)' % (
				type(self).__name__,
				', '.join('%s=%r' % t for t in attrs),
				f', **{self.kwargs}' if self.kwargs else '')
	'''
	@abc.abstractmethod
	def __call__(self):
		"""Optional[T]: Returns a trasport-specific request object,
		or ``None`` if not applicable for the transport being used.
		"""
		raise NotImplementedError
	'''

class Response(abc.ABC):
	"""An ABC that wraps a transport-specific HTTP response object."""

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

	def __init__(self, response, request=None):
		"""
		Attributes
		----------
		response: object
			The transport specific response object to wrap.
		request: Optional[:class:`Request`]
			The request adaptor as context for this response.
		"""
		self.response = response
		self.request = request


class Requestor(abc.ABC):
	"""Interface. A Requestor is a thing that makes requests."""

	@abc.abstractmethod
	def request(self, request, timeout=None):
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
