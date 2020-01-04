"""Transport adapter for Requests."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from .request import Request

from functools import partial

import requests

from ._base_session_sync import BaseSession
from .. import exceptions
from .. import payload
from ..response import Response

_PAYLOAD_DISPATCH_TABLE = {
	type(None): lambda data: {},
	payload.Raw: lambda data: dict(data=data),
	payload.FormData: lambda data: dict(data=data),
	payload.MultiPart: lambda data: dict(files=data),
	payload.Text: lambda data: dict(data=data),
	payload.JSON: lambda data: dict(json=data),
}

class Session(BaseSession):
	def __init__(self, session: requests.Session) -> None:
		super().__init__()
		self.session = session

	def request(self, request: Request, timeout: Optional[int] = 8) -> Response:
		self._prepare_request(request)

		r = request
		kwargs = {
			'method': r.verb,
			'url': r.url,
			'params': r.params,
			'headers': r.headers,
			'timeout': timeout,
		}
		kwargs_x = _PAYLOAD_DISPATCH_TABLE[type(r.data)](r.data)
		kwargs.update(kwargs_x)

		try:
			resp = self.session.request(**kwargs)
		except Exception as exc:
			raise exceptions.TransportError(exc) from exc

		return Response(
			status=resp.status_code,
			headers=resp.headers,
			data=resp.content,
			response=resp,
			request=r,
		)

	def close(self):
		self.session.close()

def new_session() -> Session:
	retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
	se = requests.Session()
	se.mount('https://', retry_adapter)
	return Session(se)
