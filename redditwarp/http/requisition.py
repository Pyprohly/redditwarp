
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Union, Any
if TYPE_CHECKING:
    from .payload import Payload, RequestFiles

from dataclasses import dataclass

from .payload import make_payload
from .util.case_insensitive_dict import CaseInsensitiveDict


@dataclass(repr=False, eq=False)
class Requisition:
    """Basically a request object designed to be mutated."""
    verb: str
    url: str
    params: MutableMapping[str, str]
    headers: MutableMapping[str, str]
    payload: Optional[Payload]


def make_requisition(
    verb: str,
    url: str,
    *,
    params: Optional[Mapping[str, str]] = None,
    headers: Optional[Mapping[str, str]] = None,
    data: Optional[Union[Mapping[str, str], bytes]] = None,
    json: Any = None,
    files: Optional[RequestFiles] = None,
) -> Requisition:
    params = dict(params or {})
    headers = CaseInsensitiveDict(headers or {})
    payload = make_payload(data, json, files)
    return Requisition(verb, url, params=params, headers=headers, payload=payload)
