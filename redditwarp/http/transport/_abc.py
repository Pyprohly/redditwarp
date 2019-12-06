"""
Interfaces used by transport adapters to support various HTTP libraries
"""

import abc

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
		response: Optional[object]
			The transport-specific response object to wrap, if applicable.
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
