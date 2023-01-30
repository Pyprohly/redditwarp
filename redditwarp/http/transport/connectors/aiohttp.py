
from __future__ import annotations
from typing import Optional

import asyncio

import aiohttp  # type: ignore[import]

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


class AiohttpConnector(Connector):
    def __init__(self,
        session: aiohttp.ClientSession,
    ) -> None:
        super().__init__()
        self.session: aiohttp.ClientSession = session

    async def _send(self, p: SendParams) -> Exchange:
        r = p.requisition

        etv = _get_effective_timeout(p.timeout)

        client_timeout = aiohttp.ClientTimeout(
            total=etv,
            connect=etv,
            sock_connect=etv,
            sock_read=etv,
        )
        if etv == -1:
            client_timeout = aiohttp.ClientTimeout(
                total=None,
                connect=None,
                sock_connect=None,
                sock_read=None,
            )

        follow_redirects = _get_effective_follow_redirects(p.follow_redirects)

        headers: dict[str, str] = dict(r.headers)
        data: object = None
        json: object = None

        pld = r.payload
        if pld is None:
            pass

        elif isinstance(pld, payload.Bytes):
            headers['Content-Type'] = pld.get_media_type()
            data = pld.data

        elif isinstance(pld, payload.Text):
            headers['Content-Type'] = pld.get_media_type()
            data = pld.text.encode()

        elif isinstance(pld, payload.JSON):
            json = pld.json

        elif isinstance(pld, payload.URLEncodedFormData):
            data = dict(pld.data)

        elif isinstance(pld, payload.MultipartFormData):
            data = aiohttp.FormData()
            for pt in pld.parts:
                if isinstance(pt, payload.MultipartFormData.TextField):
                    data.add_field(pt.name, pt.text)
                elif isinstance(pt, payload.MultipartFormData.FileField):
                    data.add_field(pt.name, pt.file, filename=pt.filename, content_type=pt.content_type)

        else:
            raise Exception(f"unsupported payload type: {pld.__class__.__name__!r}")

        try:
            async with self.session.request(
                method=r.verb,
                url=r.url,
                params=r.params,
                headers=headers,
                timeout=client_timeout,
                allow_redirects=follow_redirects,
                data=data,
                json=json,
            ) as resp:
                requ = resp.request_info
                x_requ = Request(
                    verb=requ.method,
                    url=str(requ.real_url),
                    headers=requ.headers,
                    data=b'',
                )
                x_resp = UResponse(
                    status=resp.status,
                    headers=resp.headers,
                    data=(await resp.content.read()),
                    underlying_object=resp,
                )
                history = [
                    UResponse(
                        status=resp1.status,
                        headers=resp1.headers,
                        data=(await resp1.content.read()),
                        underlying_object=resp1,
                    )
                    for resp1 in resp.history
                ]
        except asyncio.TimeoutError as cause:
            raise exceptions.TimeoutException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        return Exchange(
            requisition=r,
            request=x_requ,
            response=x_resp,
            history=history,
        )

    async def _close(self) -> None:
        await self.session.close()


def new_connector() -> AiohttpConnector:
    return AiohttpConnector(aiohttp.ClientSession())


name: str = aiohttp.__name__
version: str = aiohttp.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_connector=new_connector,
)
