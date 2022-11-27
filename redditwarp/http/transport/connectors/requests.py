
from __future__ import annotations
from typing import Optional

import requests  # type: ignore[import]
import requests.adapters  # type: ignore[import]

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


class RequestsConnector(Connector):
    def __init__(self,
        session: requests.Session,
    ) -> None:
        super().__init__()
        self.session: requests.Session = session

    def _send(self, p: SendParams) -> Exchange:
        r = p.requisition

        timeout = _get_effective_timeout(p.timeout)
        follow_redirects = _get_effective_follow_redirects(p.follow_redirects)

        extra_headers: dict[str, str] = {}
        data: object = None
        json: object = None
        files: object = None

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
            data = pld.data

        elif isinstance(pld, payload.MultipartFormData):
            text_plds: list[payload.MultipartTextField] = []
            file_plds: list[payload.MultipartFileField] = []
            for part in pld.parts:
                if isinstance(part, payload.MultipartTextField):
                    text_plds.append(part)
                elif isinstance(part, payload.MultipartFileField):
                    file_plds.append(part)

            if not file_plds:
                # Requests won't let us send a multipart if no files :(
                raise Exception('multipart without file fields not supported')

            data = {ty.name: ty.value for ty in text_plds}
            files = {
                fy.name: (fy.filename, fy.file, fy.content_type)
                for fy in file_plds
            }

        else:
            raise Exception(f'unsupported payload type: {pld.__class__.__name__!r}')

        headers = {**r.headers, **extra_headers}

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
        x_requ = Request(
            verb=requ.method or '',
            url=requ.url or '',
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

    def _close(self) -> None:
        self.session.close()


def new_connector() -> RequestsConnector:
    return RequestsConnector(requests.Session())


name: str = requests.__name__
version: str = requests.__version__
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_connector=new_connector,
)
