
from __future__ import annotations
from typing import Optional, Any

import requests  # type: ignore[import]
import requests.adapters  # type: ignore[import]

from ... import exceptions
from ... import payload
from ...send_params import SendParams
from ...exchange import Exchange
from ...request import Request
from ...response import UResponse
from ...connector_SYNC import Connector as BaseConnector


def _get_effective_timeout(v: float) -> float:
    if 0 > v != -1:
        raise ValueError(f"invalid `timeout` value: {v}")
    return v

def _get_effective_follow_redirects(v: Optional[bool]) -> bool:
    if v is None:
        raise ValueError(f"invalid `follow_redirects` value: {v}")
    return v


class RequestsConnector(BaseConnector):
    def __init__(self,
        session: requests.Session,
    ) -> None:
        super().__init__()
        self.session: requests.Session = session
        ("")

    def _send(self, p: SendParams) -> Exchange:
        r = p.requisition

        timeout = _get_effective_timeout(p.timeout)
        follow_redirects = _get_effective_follow_redirects(p.follow_redirects)

        headers: dict[str, str] = dict(r.headers)
        data: object = None
        json: object = None
        files: Any = None

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
            data = pld.data

        elif isinstance(pld, payload.MultipartFormData):
            files = {}
            for pt in pld.parts:
                if isinstance(pt, payload.MultipartFormData.TextField):
                    files[pt.name] = (None, pt.text)
                elif isinstance(pt, payload.MultipartFormData.FileField):
                    if pt.content_type == '':
                        raise ValueError('empty string multipart content type not supported')
                    files[pt.name] = (pt.filename, pt.file, pt.content_type)
                else:
                    raise ValueError('unexpected multipart field type: ' + repr(pt))

        else:
            raise Exception(f"unsupported payload type: {pld.__class__.__name__!r}")

        try:
            resp = self.session.request(
                method=r.verb,
                url=r.url,
                params=r.params,
                headers=headers,
                timeout=timeout,
                allow_redirects=follow_redirects,
                data=data,
                json=json,
                files=files,
            )
        except requests.exceptions.ReadTimeout as cause:
            raise exceptions.TimeoutException from cause
        except Exception as cause:
            raise exceptions.TransportError from cause

        requ = resp.request

        x_requ_data = requ.body
        if isinstance(x_requ_data, str):
            x_requ_data = x_requ_data.encode()
        elif x_requ_data is None:
            x_requ_data = b''

        x_requ = Request(
            verb=requ.method or '',
            url=requ.url or '',
            headers=requ.headers,
            data=x_requ_data,
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
        self.session.close()

Connector = RequestsConnector


def new_connector() -> RequestsConnector:
    return RequestsConnector(requests.Session())


name: str = requests.__name__
version: str = requests.__version__
