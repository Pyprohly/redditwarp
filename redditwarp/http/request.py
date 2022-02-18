
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Union, Any
if TYPE_CHECKING:
    from .payload import Payload, RequestFiles

from dataclasses import dataclass

from .payload import make_payload
from .util.case_insensitive_dict import CaseInsensitiveDict

@dataclass(eq=False, repr=False)
class Request:
    verb: str
    uri: str
    params: MutableMapping[str, str]
    headers: MutableMapping[str, str]
    payload: Optional[Payload]

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} [{self.verb}]>'

def make_request(
    verb: str,
    uri: str,
    *,
    params: Optional[Mapping[str, str]] = None,
    headers: Optional[Mapping[str, str]] = None,
    data: Optional[Union[Mapping[str, str], bytes]] = None,
    json: Any = None,
    files: Optional[RequestFiles] = None,
    timeout: float = -2,
) -> Request:
    params = dict(params or {})
    headers = CaseInsensitiveDict(headers or {})
    payload = make_payload(data, json, files)
    return Request(verb, uri, params=params, headers=headers, payload=payload)
