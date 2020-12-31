
from __future__ import annotations
from typing import Optional, Any, Mapping, Union, \
        AnyStr, IO, Sequence, Tuple, List, cast

import mimetypes
import os.path as op

FileObjectType = Union[IO[str], IO[bytes]]
RequestFiles = Union[
    Mapping[str, FileObjectType],
    Mapping[str, Tuple[FileObjectType]],
    Mapping[str, Tuple[FileObjectType, str]],
    Mapping[str, Tuple[FileObjectType, str, Optional[str]]],
    Sequence[Tuple[str, FileObjectType, str, Optional[str]]],
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
    def __init__(self, name: str, filename: str, file: FileObjectType,
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


def guess_content_type_from_filename(fname: str) -> str:
    return mimetypes.guess_type(fname)[0] or Bytes.CONTENT_TYPE_HINT

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
                    length = len(value)
                    if length == 1:
                        file, = cast(Tuple[FileObjectType], value)
                        filename = key
                        content_type: Optional[str] = guess_content_type_from_filename(filename)
                    if length == 2:
                        file, filename = cast(Tuple[FileObjectType, str], value)
                        content_type = guess_content_type_from_filename(filename)
                    elif length == 3:
                        file, filename, content_type = cast(Tuple[FileObjectType, str, Optional[str]], value)
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
                    body = MultipartFileData(key, filename, value, content_type)

                file_parts.append(Multipart.Part(body))

        else:
            for (name, value2, filename, content_type) in files:
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
