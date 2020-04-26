"""Transport adapter for Requests."""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Any
if TYPE_CHECKING:
	from ..request import Request

import requests

from .base_session_sync import BaseSession
from .. import exceptions
from .. import payload
from ..response import Response

_PAYLOAD_DISPATCH_TABLE: Mapping[Any, Any] = {
	type(None): lambda y: {},
	payload.Raw: lambda y: {'data': y.data},
	payload.FormData: lambda y: {'data': y.data},
	payload.MultiPart: lambda y: {'files': y.data},
	payload.Text: lambda y: {'data': y.text},
	payload.JSON: lambda y: {'json': y.json},
}


name = 'requests'
version_string = requests.__version__


class Session(BaseSession):
	def __init__(self,
		session: requests.Session,
		*,
		params: Optional[Mapping[str, str]] = None,
		headers: Optional[Mapping[str, str]] = None,
	) -> None:
		super().__init__(params=params, headers=headers)
		self.session = session

	def request(self, request: Request, timeout: Optional[int] = 8) -> Response:
		self._prepare_request(request)

		r = request
		kwargs: Any = {
			'method': r.verb,
			'url': r.uri,
			'params': r.params,
			'headers': r.headers,
			'timeout': timeout,
		}
		kwargs_x = _PAYLOAD_DISPATCH_TABLE[type(r.payload)](r.payload)
		kwargs.update(kwargs_x)

		try:
			resp = self.session.request(**kwargs)
		except requests.exceptions.ReadTimeout as e:
			raise exceptions.TimeoutError from e
		except Exception as e:
			raise exceptions.TransportError from e

		return Response(
			status=resp.status_code,
			headers=resp.headers,
			data=resp.content,
			request=r,
			underlying_object=resp,
		)

	def close(self) -> None:
		self.session.close()

def new_session(*,
	params: Optional[Mapping[str, str]] = None,
	headers: Optional[Mapping[str, str]] = None,
) -> Session:
	retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)
	se = requests.Session()
	se.mount('https://', retry_adapter)
	return Session(se, params=params, headers=headers)
