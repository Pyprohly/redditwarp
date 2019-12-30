"""Transport adapter for Requests."""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .request import Request

import sys
from functools import partial
from http import HTTPStatus

import requests

from ._ import BaseSession
from .. import exceptions
from .. import payload
from ..requestor import Requestor
from ..response import Response

_PAYLOAD_DISPATCH_TABLE = {
	type(None): lambda func, data: func(),
	payload.Raw: lambda func, data: func(data=data),
	payload.FormData: lambda func, data: func(data=data),
	payload.MultiPart: lambda func, data: func(files=data),
	payload.Text: lambda func, data: func(data=data),
	payload.JSON: lambda func, data: func(json=data),
}

class Session(BaseSession):
	def _new_session(self) -> requests.Session:
		retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
		se = requests.Session()
		se.mount('https://', retry_adapter)
		return se

	def __init__(self) -> None:
		super().__init__()
		self.session = self._new_session()

	def request(self, request: Request, timeout: Optional[int] = 8) -> Response:
		self._prepare_request(request)

		r = request
		request_func_partial = partial(
			self.session.request,
			method=r.verb,
			url=r.url,
			params=r.params,
			headers=r.headers,
			timeout=timeout,
		)

		d = r.data
		request_func = _PAYLOAD_DISPATCH_TABLE[type(d)]

		try:
			resp = request_func(request_func_partial, d)
		except requests.exceptions.RequestException as exc:
			raise exceptions.TransportError(exc) from exc

		return Response(
			status=resp.status_code,
			headers=resp.headers,
			data=resp.content,
			response=resp,
			request=r,
		)
