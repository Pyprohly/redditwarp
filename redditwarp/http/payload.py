
from __future__ import annotations
from typing import Optional, Any, Mapping, Union, \
        IO, Sequence, Tuple, cast, MutableMapping

import mimetypes
import os.path as op

FileObjectType = Union[IO[str], IO[bytes]]
RequestFiles = Union[
    Mapping[str, FileObjectType],
    Mapping[str, Tuple[FileObjectType]],
    Mapping[str, Tuple[FileObjectType, str]],
    Mapping[str, Tuple[FileObjectType, str, str]],
    Sequence[Tuple[str, FileObjectType, str, str]],
]

class Payload:
    pass

class Content(Payload):
    CONTENT_TYPE_HINT: str = ''

    def get_content_type(self) -> str:
        return self.CONTENT_TYPE_HINT

    def apply_content_type(self, headers: MutableMapping[str, str], *, field_name: str = 'Content-Type') -> None:
        headers.setdefault(field_name, self.get_content_type())

class Bytes(Content):
    CONTENT_TYPE_HINT = 'application/octet-stream'

    def __init__(self, data: bytes):
        self.data: bytes = data

class URLEncodedFormData(Content):
    CONTENT_TYPE_HINT = 'application/x-www-form-urlencoded'

    def __init__(self, data: Mapping[str, str]):
        self.data: Mapping[str, str] = data

class Text(Content):
    CONTENT_TYPE_HINT = 'text/plain'

    def __init__(self, text: str):
        self.text: str = text

class TextData(Content):
    CONTENT_TYPE_HINT = 'text/plain'

    def __init__(self, data: bytes, *, charset: str = ''):
        self.data: bytes = data
        self.charset: str = charset

    def get_content_type(self) -> str:
        return self.CONTENT_TYPE_HINT + ((x := self.charset) and f'; charset={x}')

class JSON(Content):
    CONTENT_TYPE_HINT = 'application/json'

    def __init__(self, json: Any):
        self.json: Any = json


class MultipartFormDataField(Payload):
    def __init__(self, name: str):
        self.name: str = name

class MultipartTextField(MultipartFormDataField):
    def __init__(self, name: str, value: str):
        super().__init__(name)
        self.value: str = value

class MultipartFileField(MultipartFormDataField):
    def __init__(self,
            name: str, 
            file: FileObjectType,
            filename: str,
            content_type: str):
        super().__init__(name)
        self.file: FileObjectType = file
        self.filename: str = filename
        self.content_type: str = content_type

class Multipart(Payload):
    CONTENT_TYPE_HINT = 'multipart/*'

class MultipartFormData(Multipart):
    CONTENT_TYPE_HINT = 'multipart/form-data'
    def __init__(self, parts: Sequence[MultipartFormDataField]):
        self.parts: Sequence[MultipartFormDataField] = parts


def guess_mimetype_from_filename(fname: str) -> str:
    y = mimetypes.guess_type(fname, strict=False)[0]
    return y or 'application/octet-stream'

def make_payload(
    data: Optional[Union[Mapping[str, str], bytes]] = None,
    json: Any = None,
    files: Optional[RequestFiles] = None,
) -> Optional[Payload]:
    if files is not None:
        file_parts: list[MultipartFileField] = []
        if isinstance(files, Mapping):
            for key, value in files.items():
                if isinstance(value, tuple):
                    length = len(value)
                    if length == 1:
                        file, = cast(Tuple[FileObjectType], value)
                        filename = key
                        content_type = guess_mimetype_from_filename(filename)
                    if length == 2:
                        file, filename = cast(Tuple[FileObjectType, str], value)
                        content_type = guess_mimetype_from_filename(filename)
                    elif length == 3:
                        file, filename, content_type = cast(Tuple[FileObjectType, str, str], value)

                else:
                    file = value
                    filename = op.basename(file.name)
                    content_type = guess_mimetype_from_filename(filename)

                file_parts.append(MultipartFileField(key, file, filename, content_type))

        else:
            file_parts.extend(
                MultipartFileField(name, file, filename, content_type)
                for (name, file, filename, content_type) in files
            )

        text_parts: list[MultipartTextField] = []
        if data is not None:
            if not isinstance(data, Mapping):
                raise ValueError('a mapping is expected for `data` when `files` is used')
            text_parts.extend(MultipartTextField(k, (v or '')) for k, v in data.items())

        parts = cast(list[MultipartFormDataField], text_parts) + cast(list[MultipartFormDataField], file_parts)
        return MultipartFormData(parts)

    if data is not None:
        if json is not None:
            raise ValueError("`data` and `json` are mutually exclusive parameters")

        if isinstance(data, Mapping):
            return URLEncodedFormData(data)
        if isinstance(data, bytes):
            return Bytes(data)
        raise Exception

    if json is not None:
        return JSON(json)

    return None
