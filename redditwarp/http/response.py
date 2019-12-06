
import abc

class Response:
	def __init__(self, status, headers, data: bytes, response=None, request=None):
		self.status = status
		self.headers = headers
		self.data = data
		self.response = response
		self.request = request

class ResponseAdaptor(abc.ABC):
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
