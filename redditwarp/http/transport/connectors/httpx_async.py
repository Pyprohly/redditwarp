
from __future__ import annotations
from typing import Any, Optional

import httpx  # type: ignore[import]

from ... import exceptions
from ... import payload
from ...send_params import SendParams
from ...exchange import Exchange
from ...request import Request
from ...response import UResponse
from ..reg_ASYNC import register
from ..connector_ASYNC import Connector


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
        client: httpx.AsyncClient,
    ) -> None:
        super().__init__()
        self.client: httpx.AsyncClient = client

    async def _send(self, p: SendParams) -> Exchange:
        r = p.requisition

        etv = _get_effective_timeout(p.timeout)
        timeout_obj = httpx.Timeout(etv, pool=20)
        if etv == -1:
            timeout_obj = httpx.Timeout(None, pool=20)

        follow_redirects = _get_effective_follow_redirects(p.follow_redirects)

        extra_headers: dict[str, str] = {}
        data: Any = None
        json: Any = None
        files: Any = None

        pld = r.payload
        if pld is None:
            pass

        elif isinstance(pld, payload.Bytes):
            pld.apply_content_type_header(extra_headers)
            data = pld.data

        elif isinstance(pld, payload.Text):
            pld.apply_content_type_header(extra_headers)
            data = pld.text.encode()

        elif isinstance(pld, payload.JSON):
            json = pld.json

        elif isinstance(pld, payload.URLEncodedFormData):
            data = dict(pld.data)

        elif isinstance(pld, payload.MultipartFormData):
            text_plds: list[payload.MultipartTextField] = []
            file_plds: list[payload.MultipartFileField] = []
            for part in pld.parts:
                if isinstance(part, payload.MultipartTextField):
                    text_plds.append(part)
                elif isinstance(part, payload.MultipartFileField):
                    file_plds.append(part)

            if not file_plds:
                # Httpx won't let us send a multipart if no files :(
                raise Exception('multipart without file fields not supported')

            data = {ty.name: ty.value for ty in text_plds}
            files = {
                fy.name: (fy.filename, fy.file, fy.content_type)
                for fy in file_plds
            }

        else:
            raise Exception('unsupported payload type')

        headers = {**r.headers, **extra_headers}

        try:
            resp = await self.client.request(
                method=r.verb,
                url=r.url,
                params=r.params,
                headers=headers,
                timeout=timeout_obj,
                follow_redirects=follow_redirects,
                data=data,
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

    async def _close(self) -> None:
        await self.client.aclose()


def new_connector() -> HttpxConnector:
    return HttpxConnector(httpx.AsyncClient())


name: str = httpx.__name__
version: str = httpx.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_connector=new_connector,
)
