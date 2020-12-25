
from __future__ import annotations
from typing import Optional, Any, Mapping, Union, \
        AnyStr, IO, Sequence, Tuple, List, cast
from io import IOBase

import mimetypes
import os.path as op

RequestFiles = Union[
    Mapping[str, Union[IO[str], IO[bytes]]],
    Mapping[str, Tuple[str, IOBase]],
    Mapping[str, Tuple[str, IOBase, Optional[str]]],
    Sequence[Tuple[str, str, IOBase, Optional[str]]],
]

class Payload:
    pass

class CommonContentType(Payload):
    CONTENT_TYPE_HINT = ''


class Bytes(CommonContentType):
    CONTENT_TYPE_HINT = 'application/octet-stream'
    def __init__(self, data: bytes):
        self.data = data

class FormData(CommonContentType):
    CONTENT_TYPE_HINT = 'application/x-www-form-urlencoded'
    def __init__(self, data: Mapping[str, str]):
        self.data = data

class Text(CommonContentType):
    CONTENT_TYPE_HINT = 'text/plain'
    def __init__(self, text: str):
        self.text = text

class JSON(CommonContentType):
    CONTENT_TYPE_HINT = 'application/json'
    def __init__(self, json: Any):
        self.json = json


class MultipartDataField(Payload):
    def __init__(self, name: str):
        self.name = name

class MultipartTextData(MultipartDataField):
    def __init__(self, name: str, value: str):
        super().__init__(name)
        self.value = value

class MultipartFileData(MultipartDataField):
    def __init__(self, name: str, filename: str, file: IOBase,
            content_type: Optional[str] = '.'):
        super().__init__(name)
        self.filename = filename
        self.file = file
        self.content_type = content_type

class Multipart(CommonContentType):
    class Part:
        CONTENT_DISPOSITION = 'form-data'
        def __init__(self, payload: Payload, headers: Optional[Mapping[str, str]] = None):
            self.headers = {} if headers is None else headers
            self.payload = payload

    CONTENT_TYPE_HINT = 'multipart/'
    def __init__(self, parts: Sequence[Part]):
        self.parts = parts


def guess_content_type_from_filename(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or Bytes.CONTENT_TYPE_HINT

def build_payload(
    data: Optional[Union[Mapping[str, str], AnyStr]] = None,
    json: Any = None,
    files: Optional[RequestFiles] = None,
) -> Optional[Payload]:
    if files is not None:
        file_parts: List[Multipart.Part] = []
        if isinstance(files, Mapping):
            for key, value in files.items():
                if isinstance(value, tuple):
                    if len(value) == 2:
                        filename, file = cast(Tuple[str, IOBase], value)
                        content_type: Optional[str] = guess_content_type_from_filename(filename)
                    elif len(value) == 3:
                        filename, file, content_type = cast(Tuple[str, IOBase, Optional[str]], value)
                        if content_type == '.':
                            content_type = guess_content_type_from_filename(filename)
                        elif content_type == '..':
                            content_type = '.'
                    else:
                        raise Exception

                    body = MultipartFileData(key, filename, file, content_type)
                else:
                    filename = op.basename(value.name)
                    content_type = guess_content_type_from_filename(filename)
                    body = MultipartFileData(key, filename, cast(IOBase, value), content_type)

                file_parts.append(Multipart.Part(body))

        else:
            for (name, filename, value2, content_type) in files:
                body = MultipartFileData(name, filename, value2, content_type)
                file_parts.append(Multipart.Part(body))

        text_parts: List[Multipart.Part] = []
        if data is not None:
            if not isinstance(data, Mapping):
                raise Exception

            for key, value3 in data.items():
                body2 = MultipartTextData(key, value3)
                text_parts.append(Multipart.Part(body2))

        return Multipart(text_parts + file_parts)

    if data is not None:
        if isinstance(data, Mapping):
            return FormData(data)
        if isinstance(data, str):
            return Text(data)
        if isinstance(data, bytes):
            return Bytes(data)
        raise Exception

    if json is not None:
        return JSON(json)

    return None
