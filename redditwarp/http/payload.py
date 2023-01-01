
from __future__ import annotations
from typing import Optional, Any, Mapping, Union, \
        IO, Sequence, cast, MutableMapping, ClassVar

import mimetypes
import os.path as op
from itertools import chain

RequestFiles = Union[
    Mapping[str, IO[bytes]],
    Mapping[str, tuple[IO[bytes]]],
    Mapping[str, tuple[IO[bytes], str]],
    Mapping[str, tuple[IO[bytes], str, str]],
    Sequence[tuple[str, IO[bytes], str, str]],
]


class Payload:
    pass


class Content(Payload):
    CONTENT_TYPE_HEADER_NAME: ClassVar[str] = 'Content-Type'
    CONTENT_TYPE_HINT: ClassVar[str] = ''

    def get_content_type(self) -> str:
        return self.CONTENT_TYPE_HINT

    def apply_content_type_header(self, headers: MutableMapping[str, str], *,
            header_name: str = CONTENT_TYPE_HEADER_NAME) -> None:
        headers.setdefault(header_name, self.get_content_type())

class Bytes(Content):
    CONTENT_TYPE_HINT: ClassVar[str] = 'application/octet-stream'

    def __init__(self, data: bytes) -> None:
        self.data: bytes = data

class Text(Content):
    CONTENT_TYPE_HINT: ClassVar[str] = 'text/plain'

    def __init__(self, text: str) -> None:
        self.text: str = text

class URLEncodedFormData(Content):
    CONTENT_TYPE_HINT: ClassVar[str] = 'application/x-www-form-urlencoded'

    def __init__(self, data: Mapping[str, str]) -> None:
        self.data: Mapping[str, str] = data

class JSON(Content):
    CONTENT_TYPE_HINT: ClassVar[str] = 'application/json'

    def __init__(self, json: Any) -> None:
        self.json: Any = json



class MultipartFormDataField:
    def __init__(self, name: str) -> None:
        self.name: str = name

class MultipartTextField(MultipartFormDataField):
    def __init__(self, name: str, value: str) -> None:
        super().__init__(name)
        self.value: str = value

class MultipartFileField(MultipartFormDataField):
    def __init__(self,
            name: str,
            file: IO[bytes],
            filename: str,
            content_type: str) -> None:
        super().__init__(name)
        self.file: IO[bytes] = file
        self.filename: str = filename
        self.content_type: str = content_type


class Multipart(Payload):
    CONTENT_TYPE_HINT: ClassVar[str] = 'multipart/*'

class MultipartFormData(Multipart):
    CONTENT_TYPE_HINT: ClassVar[str] = 'multipart/form-data'

    def __init__(self, parts: Sequence[MultipartFormDataField]) -> None:
        self.parts: Sequence[MultipartFormDataField] = parts



def guess_mimetype_from_filename(filename: str) -> str:
    y = mimetypes.guess_type(filename, strict=False)[0]
    return y or 'application/octet-stream'

def make_multipart_form_data_payload(
    data: Optional[Mapping[str, str]],
    files: RequestFiles,
) -> MultipartFormData:
    file_parts: list[MultipartFileField] = []
    if isinstance(files, Mapping):
        for key, value in files.items():
            if isinstance(value, tuple):
                length = len(value)
                if length == 1:
                    file, = cast(tuple[IO[bytes]], value)
                    filename = key
                    content_type = guess_mimetype_from_filename(filename)
                elif length == 2:
                    file, filename = cast(tuple[IO[bytes], str], value)
                    content_type = guess_mimetype_from_filename(filename)
                else:
                    file, filename, content_type = cast(tuple[IO[bytes], str, str], value)

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
        text_parts.extend(MultipartTextField(k, v) for k, v in data.items())

    parts: list[MultipartFormDataField] = list(chain(text_parts, file_parts))
    return MultipartFormData(parts)

def make_payload(
    data: Optional[Union[Mapping[str, str], bytes]] = None,
    json: Any = None,
    files: Optional[RequestFiles] = None,
) -> Optional[Payload]:
    if files is not None:
        if json is not None:
            raise TypeError("`json` and `files` are mutually exclusive parameters")
        if isinstance(data, bytes):
            raise TypeError("`data` cannot be bytes when `files` is used")
        return make_multipart_form_data_payload(data, files)

    if data is not None:
        if json is not None:
            raise TypeError("`json` and `data` are mutually exclusive parameters")
        if isinstance(data, Mapping):
            return URLEncodedFormData(data)
        return Bytes(data)

    if json is not None:
        return JSON(json)

    return None
