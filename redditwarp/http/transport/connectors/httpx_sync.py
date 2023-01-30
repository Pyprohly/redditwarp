
from __future__ import annotations
from typing import Any, Optional

import httpx  # type: ignore[import]

from ... import exceptions
from ... import payload
from ...send_params import SendParams
from ...exchange import Exchange
from ...request import Request
from ...response import UResponse
from ..reg_SYNC import register
from ..connector_SYNC import Connector


def _get_effective_timeout(v: float) -> float:
    if 0 > v != -1:
        raise ValueError(f"invalid `timeout` value: {v}")
    return v

def _get_effective_follow_redirects(v: Optional[bool]) -> bool:
    if v is None:
        raise ValueError(f"invalid `follow_redirects` value: {v}")
    return v


class HttpxConnector(Connector):
    def __init__(self,
        client: httpx.Client,
    ) -> None:
        super().__init__()
        self.client: httpx.Client = client

    def _send(self, p: SendParams) -> Exchange:
        r = p.requisition

        etv = _get_effective_timeout(p.timeout)
        timeout_obj = httpx.Timeout(etv, pool=20)
        if etv == -1:
            timeout_obj = httpx.Timeout(None, pool=20)

        follow_redirects = _get_effective_follow_redirects(p.follow_redirects)

        headers: dict[str, str] = dict(r.headers)
        data: Any = None
        content: Optional[bytes] = None
        json: Any = None
        files: Any = None

        pld = r.payload
        if pld is None:
            pass

        elif isinstance(pld, payload.Bytes):
            headers['Content-Type'] = pld.get_media_type()
            content = pld.data

        elif isinstance(pld, payload.Text):
            headers['Content-Type'] = pld.get_media_type()
            data = pld.text.encode()

        elif isinstance(pld, payload.JSON):
            json = pld.json

        elif isinstance(pld, payload.URLEncodedFormData):
            data = dict(pld.data)

        elif isinstance(pld, payload.MultipartFormData):
            files = {}
            for pt in pld.parts:
                if isinstance(pt, payload.MultipartFormData.TextField):
                    files[pt.name] = (None, pt.text.encode(), None)
                elif isinstance(pt, payload.MultipartFormData.FileField):
                    files[pt.name] = (pt.filename, pt.file, pt.content_type)

        else:
            raise Exception(f"unsupported payload type: {pld.__class__.__name__!r}")

        try:
            resp = self.client.request(
                method=r.verb,
                url=r.url,
                params=r.params,
                headers=headers,
                timeout=timeout_obj,
                follow_redirects=follow_redirects,
                data=data,
                content=content,
                json=json,
                files=files,
            )
        except httpx.TimeoutException as cause:
            raise exceptions.TimeoutException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        requ = resp.request
        x_requ = Request(
            verb=requ.method,
            url=str(requ.url),
            headers=requ.headers,
            data=requ.read(),
        )
        x_resp = UResponse(
            status=resp.status_code,
            headers=resp.headers,
            data=resp.content,
            underlying_object=resp,
        )
        history = [
            UResponse(
                status=resp1.status_code,
                headers=resp1.headers,
                data=resp1.content,
                underlying_object=resp1,
            )
            for resp1 in resp.history
        ]
        return Exchange(
            requisition=r,
            request=x_requ,
            response=x_resp,
            history=history,
        )

    def _close(self) -> None:
        self.client.close()


def new_connector() -> HttpxConnector:
    return HttpxConnector(httpx.Client())


name: str = httpx.__name__
version: str = httpx.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_connector=new_connector,
)
