
from __future__ import annotations
from typing import Any, Optional

import sys
import urllib.request
import urllib.parse
import urllib.error
import socket
import json

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


class PythonUrllibConnector(Connector):
    def _send(self, p: SendParams) -> Exchange:
        r = p.requisition

        etv = _get_effective_timeout(p.timeout)
        t = None if etv == -1 else etv

        follow_redirects = _get_effective_follow_redirects(p.follow_redirects)
        if not follow_redirects:
            raise RuntimeError('Python urllib does not support `follow_redirects=False`')

        url = merge_query_params(r.url, r.params)

        headers: dict[str, str] = dict(r.headers)
        data: Any = None

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
            headers['Content-Type'] = pld.get_media_type()
            data = json.dumps(pld.json).encode()

        elif isinstance(pld, payload.URLEncodedFormData):
            data = urllib.parse.urlencode(pld.data).encode()

        elif isinstance(pld, payload.MultipartFormData):
            raise Exception('multipart payload not supported by python urllib')

        else:
            raise Exception(f"unsupported payload type: {pld.__class__.__name__!r}")

        req = urllib.request.Request(
            method=r.verb,
            url=url,
            data=data,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=t) as resp:
                content = resp.read()
        except socket.timeout as cause:
            raise exceptions.TimeoutException from cause
        except urllib.error.URLError as cause:
            if str(cause.reason) == 'timed out':
                raise exceptions.TimeoutException from cause
            raise
        except Exception as cause:
            raise exceptions.TransportError from cause

        x_requ = Request(
            verb=r.verb,
            url=url,
            headers={},
        )
        x_resp = UResponse(
            status=resp.status,
            headers=resp.headers,
            data=content,
            underlying_object=resp,
        )
        return Exchange(
            requisition=r,
            request=x_requ,
            response=x_resp,
            history=(),
        )

    def _close(self) -> None:
        pass


def new_connector() -> PythonUrllibConnector:
    return PythonUrllibConnector()


name: str = 'python-urllib'
version: str = '%d.%d' % sys.version_info[:2]
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_connector=new_connector,
)
