
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import Optional, Any
	from collections.abc import Mapping
	from .request import Request

from dataclasses import dataclass

@dataclass
class Response:
	status: int
	headers: Mapping[str, str]
	data: bytes
	request: Optional[Request] = None
	transport_response: Optional[Any] = None

	def __repr__(self):
		return f'<{self.__class__.__name__} [{self.status}]>'
