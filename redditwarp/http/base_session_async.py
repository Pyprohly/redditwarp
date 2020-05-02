
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Type
	from types import TracebackType
	from collections.abc import Mapping
	from .request import Request
	from .response import Response

from .requestor_async import Requestor

class BaseSession(Requestor):
	def __init__(self,
		*,
		params: Optional[Mapping[str, str]] = None,
		headers: Optional[Mapping[str, str]] = None,
	) -> None:
		self.params = {} if params is None else params
		self.headers = {} if headers is None else headers

	async def __aenter__(self):
		return self

	async def __aexit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		await self.close()
		return None

	def _prepare_request(self, request: Request) -> None:
		h = request.headers
		h.update({**self.headers, **h})
		p = request.params
		p.update({**self.params, **p})

	async def request(self, request: Request, *, timeout: Optional[float] = None,
			auxiliary: Optional[Mapping] = None) -> Response:
		raise NotImplementedError

	async def close(self) -> None:
		pass
