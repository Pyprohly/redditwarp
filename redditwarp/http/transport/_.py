
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .request import Request

from ..requestor import Requestor

TIMEOUT = 8

class BaseSession(Requestor):
	"""
	Attributes
	----------
	headers: :class:`CaseInsensitiveDict`[str, Union[str, bytes]]
		A case-insensitive dictionary of headers to be sent on each Request.
	params: Dict[str, Union[str, bytes]]
		Dictionary of querystring data to attach to each Request.
	"""
	def __init__(self) -> None:
		self.headers = {}
		self.params = {}

	def _prepare_request(self, request: Request) -> None:
		# No clobber dict update
		h = request.headers
		h.update({**self.headers, **h})
		p = request.params
		p.update({**self.params, **p})

	def request(self, request: Request, timeout: int = TIMEOUT) -> Response:
		raise NotImplementedError

	def close(self) -> None:
		raise NotImplementedError
