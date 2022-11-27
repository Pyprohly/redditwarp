
from __future__ import annotations
from typing import Optional, Union

import json

import urllib3  # type: ignore[import]
import urllib3.exceptions as urllib3_exceptions  # type: ignore[import]

from ... import exceptions
from ... import payload
from ...send_params import SendParams
from ...exchange import Exchange
from ...request import Request
from ...response import UResponse
from ..reg_SYNC import register
from ..connector_SYNC import Connector
from ...util.merge_query_params import merge_query_params


def _get_effective_timeout(v: float) -> float:
    if 0 > v != -1:
        raise ValueError(f"invalid `timeout` value: {v}")
    return v

def _get_effective_follow_redirects(v: Optional[bool]) -> bool:
    if v is None:
        raise ValueError(f"invalid `follow_redirects` value: {v}")
    return v


class Urllib3Connector(Connector):
    def __init__(self,
        http: urllib3.poolmanager.PoolManager,
    ) -> None:
        super().__init__()
        self.http: urllib3.poolmanager.PoolManager = http

    def _send(self, p: SendParams) -> Exchange:
        r = p.requisition

        etv = _get_effective_timeout(p.timeout)
        tmo = None if etv == -1 else etv

        follow_redirects = _get_effective_follow_redirects(p.follow_redirects)

        url = merge_query_params(r.url, r.params)
        headers = dict(r.headers)
        pld = r.payload

        resp: urllib3.response.HTTPResponse
        try:
            if pld is None:
                resp = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.Bytes):
                pld.apply_content_type_header(headers)
                resp = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    body=pld.data,
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.Text):
                pld.apply_content_type_header(headers)
                resp = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    body=pld.text.encode(),
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.JSON):
                pld.apply_content_type_header(headers)
                resp = self.http.urlopen(
                    r.verb,
                    url,
                    headers=headers,
                    body=json.dumps(pld.json).encode(),
                    timeout=tmo,
                    redirect=follow_redirects,
                )

            elif isinstance(pld, payload.URLEncodedFormData):
                fields0: dict[str, str] = dict(pld.data)
                resp = self.http.request_encode_body(
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

                resp = self.http.request_encode_body(
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

        x_resp = UResponse(
            status=resp.status,
            headers=resp.headers,
            data=resp.data,
            underlying_object=resp,
        )
        return Exchange(
            requisition=r,
            request=Request('', '', {}),
            response=x_resp,
            history=(),
        )

    def _close(self) -> None:
        self.http.clear()


def new_connector() -> Urllib3Connector:
    return Urllib3Connector(urllib3.PoolManager())


name: str = urllib3.__name__
version: str = urllib3.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_connector=new_connector,
)
