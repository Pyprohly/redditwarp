
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Type
	from types import TracebackType
	from collections.abc import Mapping
	from .request import Request
	from .response import Response

from .requestor import Requestor

class BaseSession(Requestor):
	"""
	Attributes
	----------
	headers: :class:`CaseInsensitiveDict`[str, Union[str, bytes]]
		A case-insensitive dictionary of headers to be sent on each Request.
	params: Dict[str, Union[str, bytes]]
		Dictionary of querystring data to attach to each Request.
	"""

	def __init__(self,
		*,
		params: Optional[Mapping[str, str]] = None,
		headers: Optional[Mapping[str, str]] = None,
	) -> None:
		self.params = {} if params is None else params
		self.headers = {} if headers is None else headers

	def __enter__(self) -> BaseSession:
		return self

	def __exit__(self,
		exc_type: Optional[Type[BaseException]],
		exc_value: Optional[BaseException],
		traceback: Optional[TracebackType],
	) -> Optional[bool]:
		self.close()
		return None

	def _prepare_request(self, request: Request) -> None:
		h = request.headers
		h.update({**self.headers, **h})
		p = request.params
		p.update({**self.params, **p})

	def request(self, request: Request, *, timeout: Optional[float] = None,
			auxiliary: Optional[Mapping] = None) -> Response:
		"""
		Parameters
		----------
		timeout: Optional[float]
			The connect timeout. The number of seconds the client will
			wait to establish a connection to the server.

			A None value will use a default that is specific to the transport
			adaptor. A negative number will wait an infinite amount of time.
		auxiliary: Optional[Mapping[Any, Any]]
			Additional information to be consumed by a custom :class:`BaseSession` class.
		"""
		raise NotImplementedError

	def close(self) -> None:
		pass
