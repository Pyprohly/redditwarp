
from __future__ import annotations
from typing import Optional, Any, Mapping, Union, AnyStr

class Payload:
    CONTENT_TYPE_SUGGESTION = ''

class Raw(Payload):
    CONTENT_TYPE_SUGGESTION = 'application/octet-stream'
    def __init__(self, data: bytes):
        self.data = data

class FormData(Payload):
    CONTENT_TYPE_SUGGESTION = 'application/x-www-form-urlencoded'
    def __init__(self, data: Mapping[str, str]):
        self.data = data

class MultiPart(Payload):
    CONTENT_TYPE_SUGGESTION = 'multipart/form-data'
    def __init__(self, data: Any):
        self.data = data

class Text(Payload):
    CONTENT_TYPE_SUGGESTION = 'text/plain'
    def __init__(self, text: str):
        self.text = text

class JSON(Payload):
    CONTENT_TYPE_SUGGESTION = 'application/json'
    def __init__(self, json: Any):
        self.json = json


def make_payload(
    payload: Optional[Payload] = None,
    data: Optional[Union[Mapping[str, str], AnyStr]] = None,
    json: Any = None,
) -> Optional[Payload]:
    if payload is not None:
        return payload

    if data is not None:
        if isinstance(data, Mapping):
            return FormData(data)
        if isinstance(data, str):
            return Text(data)
        if isinstance(data, bytes):
            return Raw(data)
        raise Exception

    if json is not None:
        return JSON(json)

    return None
