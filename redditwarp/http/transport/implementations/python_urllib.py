
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Iterable
if TYPE_CHECKING:
    from ...request import Request
    from ...response import Response

import sys
import urllib.request
import urllib.parse
import urllib.error
import socket
import json

from .._SYNC_ import register
from ...session_base_SYNC import SessionBase
from ... import exceptions
from ... import payload
from ...response import UResponse
from ...util.merge_query_params import merge_query_params
from ...util.case_insensitive_dict import CaseInsensitiveDict

def _generate_request_kwargs(r: Request) -> Iterable[tuple[str, Any]]:
    yield ('method', r.verb)
    url = merge_query_params(r.uri, r.params)
    yield ('url', url)

    headers = dict(r.headers)
    pld = r.payload
    if pld is None:
        pass

    elif isinstance(pld, payload.Bytes):
        pld.apply_content_type(headers)
        yield ('data', pld.data)

    elif isinstance(pld, payload.Text):
        pld.apply_content_type(headers)
        yield ('data', pld.text.encode())

    elif isinstance(pld, payload.TextData):
        pld.apply_content_type(headers)
        yield ('data', pld.data)

    elif isinstance(pld, payload.JSON):
        yield ('data', json.dumps(pld.json).encode())
        headers['Content-Type'] = 'application/json'

    elif isinstance(pld, payload.URLEncodedFormData):
        yield ('data', urllib.parse.urlencode(pld.data).encode())

    elif isinstance(pld, payload.MultipartFormData):
        raise Exception('multipart payload not supported by python urllib')

    else:
        raise Exception('unsupported payload type')

    yield ('headers', headers)


class Session(SessionBase):
    def __init__(self) -> None:
        super().__init__()

    def send(self, request: Request, *, timeout: float = -2) -> Response:
        etv = self._get_effective_timeout_value(timeout)
        kwargs = dict(_generate_request_kwargs(request))
        req = urllib.request.Request(**kwargs)
        t = None if etv == -1 else etv
        try:
            with urllib.request.urlopen(req, timeout=t) as response:
                content = response.read()
        except socket.timeout as cause:
            raise exceptions.TimeoutException from cause
        except urllib.error.URLError as cause:
            if str(cause.reason) == 'timed out':
                raise exceptions.TimeoutException from cause
            raise
        except Exception as cause:
            raise exceptions.TransportError from cause

        return UResponse(
            status=response.status,
            headers=CaseInsensitiveDict(dict(response.headers)),
            data=content,
            underlying_object=response,
        )

    def close(self) -> None:
        pass

def new_session() -> Session:
    return Session()

name: str = 'python-urllib'
version: str = '%d.%d' % sys.version_info[:2]
register(
    adaptor_module_name=__name__,
    name=name,
    version=version,
    new_session=new_session,
)
