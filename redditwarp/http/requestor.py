
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .request import Request
	from .response import Response
	from .requestor import Requestor

class Requestor:
	"""Interface. A Requestor is a thing that makes requests."""

	def request(self, request: Request, timeout: Optional[int]) -> Response:
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
	def __init__(self, requestor: Requestor) -> None:
		self.requestor = requestor

	def request(self, request: Request, timeout: Optional[int]) -> Response:
		return self.requestor.request(request, timeout)
