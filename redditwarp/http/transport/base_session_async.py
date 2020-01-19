
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Type
	from types import TracebackType
	from .request import Request
	from .response import Response

from ..requestor import Requestor

class BaseSession(Requestor):
	def __init__(self) -> None:
		self.headers = {}
		self.params = {}

	async def __aenter__(self) -> BaseSession:
		return self

	async def __aexit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		await self.close()

	def _prepare_request(self, request: Request) -> None:
		h = request.headers
		h.update({**self.headers, **h})
		p = request.params
		p.update({**self.params, **p})

		for d in h, p:
			d2 = {k: v for k, v in d.items() if v is not None}
			d.clear()
			d.update(d2)

	async def request(self, request: Request, timeout: Optional[int] = 8) -> Response:
		raise NotImplementedError

	async def close(self) -> None:
		pass
