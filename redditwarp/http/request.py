
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, MutableMapping, Union, AnyStr, Any
if TYPE_CHECKING:
    from .payload import Payload, RequestFiles

from dataclasses import dataclass, field

from .payload import make_payload
from .util.join_params_ import join_params

@dataclass(eq=False)
class Request:
    verb: str
    uri: str
    params: MutableMapping[str, Optional[str]] = field(default_factory=dict)
    headers: MutableMapping[str, str] = field(default_factory=dict)
    payload: Optional[Payload] = None

    def get_url(self) -> str:
        return join_params(self.uri, self.params)

def make_request(
    verb: str,
    uri: str,
    *,
    params: Optional[Mapping[str, Optional[str]]] = None,
    headers: Optional[Mapping[str, str]] = None,
    data: Optional[Union[Mapping[str, str], AnyStr]] = None,
    json: Any = None,
    files: Optional[RequestFiles] = None,
    timeout: float = -2,
    aux_info: Optional[Mapping[Any, Any]] = None,
) -> Request:
    params = dict({} if params is None else params)
    headers = dict({} if headers is None else headers)
    payload = make_payload(data, json, files)
    return Request(verb, uri, params=params, headers=headers, payload=payload)
