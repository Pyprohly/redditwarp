
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional
	from .request import Request
	from .response import Response

from ..requestor import Requestor

class BaseSession(Requestor):
	def __init__(self) -> None:
		self.headers = {}
		self.params = {}

	def _prepare_request(self, request: Request) -> None:
		# No clobber dict update
		h = request.headers
		h.update({**self.headers, **h})
		p = request.params
		p.update({**self.params, **p})

	async def request(self, request: Request, timeout: Optional[int] = 8) -> Response:
		raise NotImplementedError
