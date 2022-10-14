
# type: ignore[no-untyped-call]

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Iterable
if TYPE_CHECKING:
    from ...request import Request
    from ...response import Response

import json

import urllib3  # type: ignore[import]
import urllib3.exceptions as urllib3_exceptions  # type: ignore[import]

from ..SYNC import register
from ...session_base_SYNC import SessionBase
from ... import exceptions
from ... import payload
from ...response import UResponse
from ...util.merge_query_params import merge_query_params

def _get_effective_timeout_value(timeouts: Iterable[float]) -> float:
    for tv in timeouts:
        if tv == -2:
            continue
        if 0 > tv != -1:
            raise ValueError('invalid timeout value: %s' % tv)
        return tv
    raise ValueError('a default timeout value could not be determined')

class Session(SessionBase):
    def __init__(self,
        http: urllib3.poolmanager.PoolManager,
    ) -> None:
        super().__init__()
        self.http: urllib3.poolmanager.PoolManager = http

    def send(self, request: Request, *,
            timeout: float = -2, follow_redirects: Optional[bool] = None) -> Response:
        etv = _get_effective_timeout_value((timeout, self.timeout))
        tmo: Optional[float] = etv
        if tmo == -1:
            tmo = None

        follow_redirects = self.follow_redirects if follow_redirects is None else follow_redirects

        r = request
        url = merge_query_params(r.uri, r.params)
        headers = dict(r.headers)
        pld = r.payload

        response: urllib3.response.HTTPResponse
        try:
            if pld is None:
                response = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.Bytes):
                pld.apply_content_type(headers)
                response = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    body=pld.data,
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.Text):
                pld.apply_content_type(headers)
                response = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    body=pld.text.encode(),
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.JSON):
                pld.apply_content_type(headers)
                response = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    body=json.dumps(pld.json).encode(),
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.URLEncodedFormData):
                fields0: dict[str, str] = dict(pld.data)
                response = self.http.request_encode_body(
                    r.verb,
                    url,
                    headers=headers,
                    fields=fields0,
                    timeout=tmo,
                    redirect=follow_redirects,
                    encode_multipart=False,
                )

            elif isinstance(pld, payload.MultipartFormData):
                fields: dict[str, Union[str, tuple[str, Union[str, bytes], str]]] = {}
                for part in pld.parts:
                    if isinstance(part, payload.MultipartTextField):
                        fields[part.name] = part.value
                    elif isinstance(part, payload.MultipartFileField):
                        fields[part.name] = (part.filename, part.file.read(), part.content_type)

                response = self.http.request_encode_body(
                    r.verb,
                    url,
                    headers=headers,
                    fields=fields,
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            else:
                raise Exception('unsupported payload type')

        except urllib3_exceptions.ReadTimeoutError as cause:
            raise exceptions.TimeoutException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        return UResponse(
            status=response.status,
            headers=response.headers,
            data=response.data,
            underlying_object=response,
        )

    def close(self) -> None:
        self.http.clear()

def new_session() -> Session:
    http = urllib3.PoolManager()
    return Session(http)

name: str = urllib3.__name__
version: str = urllib3.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
