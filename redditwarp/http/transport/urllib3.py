
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
if TYPE_CHECKING:
    from ..request import Request
    from ..response import Response

import json

import urllib3  # type: ignore[import]

from .SYNC import register
from ..session_base_SYNC import SessionBase
from .. import exceptions
from .. import payload
from ..response import UResponse
from ..util.merge_query_params import merge_query_params

class Session(SessionBase):
    def __init__(self,
        http: urllib3.PoolManager,
    ) -> None:
        super().__init__()
        self.http = http

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        etv = self._get_effective_timeout_value(timeout)
        tmo: Optional[float] = etv
        if tmo == -1:
            tmo = None

        r = request
        url = merge_query_params(r.uri, r.params)
        headers = dict(r.headers)
        pld = r.payload

        response: urllib3.response.HTTPResponse
        try:
            if pld is None:
                response = self.http.urlopen(r.verb, url, headers=headers, timeout=tmo)

            elif isinstance(pld, payload.Bytes):
                pld.apply_content_type(headers)
                response = self.http.urlopen(r.verb, url, headers=headers, body=pld.data, timeout=tmo)

            elif isinstance(pld, payload.Text):
                pld.apply_content_type(headers)
                response = self.http.urlopen(r.verb, url, headers=headers, body=pld.text.encode(), timeout=tmo)

            elif isinstance(pld, payload.TextData):
                pld.apply_content_type(headers)
                response = self.http.urlopen(r.verb, url, headers=headers, body=pld.data, timeout=tmo)

            elif isinstance(pld, payload.JSON):
                pld.apply_content_type(headers)
                response = self.http.urlopen(r.verb, url, headers=headers, body=json.dumps(pld.json).encode(), timeout=tmo)

            elif isinstance(pld, payload.URLEncodedFormData):
                fields0: dict[str, str] = dict(pld.data)
                response = self.http.request_encode_body(r.verb, url, headers=headers, fields=fields0, timeout=tmo)

            elif isinstance(pld, payload.MultipartFormData):
                fields: dict[str, Union[str, tuple[str, payload.FileObjectType, str]]] = {}
                for part in pld.parts:
                    if isinstance(part, payload.MultipartTextField):
                        fields[part.name] = part.value
                    elif isinstance(part, payload.MultipartFileField):
                        fields[part.name] = (part.filename, part.file, part.content_type)

                response = self.http.request_encode_body(r.verb, url, headers=headers, fields=fields, timeout=tmo)

            else:
                raise Exception('unsupported payload type')

        except urllib3.exceptions.MaxRetryError as e:
            raise exceptions.TimeoutException from e
        except Exception as e:
            raise exceptions.TransportError from e

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

name = urllib3.__name__
version = urllib3.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
