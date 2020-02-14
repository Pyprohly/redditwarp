
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Dict, Any
	from .request import Request

class Response:
	def __init__(self, status: int, headers: Dict[str, str], data: bytes,
			request: Optional[Request] = None, response: Optional[Any] = None):
		self.status = status
		self.headers = headers
		self.data = data
		self.request = request
		self.response = response

	def __repr__(self):
		return f'<{self.__class__.__name__} [{self.status}]>'
