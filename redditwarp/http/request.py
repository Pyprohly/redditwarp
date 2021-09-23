
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Union, Any
if TYPE_CHECKING:
    from .payload import Payload, RequestFiles

from dataclasses import dataclass, field

from .payload import make_payload

@dataclass(eq=False)
class Request:
    verb: str
    uri: str
    params: MutableMapping[str, str] = field(default_factory=dict)
    headers: MutableMapping[str, str] = field(default_factory=dict)
    payload: Optional[Payload] = None

BLANK_REQUEST = Request('', '')

def make_request(
    verb: str,
    uri: str,
    *,
    params: Optional[Mapping[str, str]] = None,
    headers: Optional[Mapping[str, str]] = None,
    data: Optional[Union[Mapping[str, str], str, bytes]] = None,
    json: Any = None,
    files: Optional[RequestFiles] = None,
    timeout: float = -2,
) -> Request:
    params = dict(params or {})
    headers = dict(headers or {})
    payload = make_payload(data, json, files)
    return Request(verb, uri, params=params, headers=headers, payload=payload)
