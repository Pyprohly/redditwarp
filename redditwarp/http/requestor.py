
import abc

TIMEOUT = 8

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

class RequestorDecorator(Requestor):
	def __init__(self, requestor):
		self.requestor = requestor

	def request(self, request, **kwargs):
		return self.requestor.request(request, **kwargs)
