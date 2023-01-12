
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Union, \
        IO, Sequence, ClassVar
if TYPE_CHECKING:
    from ..types import JSON_ro

from dataclasses import dataclass

from .types import RequestFiles
from .util.guess_filename_mimetype import guess_filename_mimetype as guess_filename_mimetype  # noqa: F401


class Payload:
    pass

class Content(Payload):
    CONTENT_TYPE_HEADER_NAME: ClassVar[str] = 'Content-Type'
    MEDIA_TYPE_HINT: ClassVar[str] = 'application/octet-stream'

    def get_media_type(self) -> str:
        return self.MEDIA_TYPE_HINT

@dataclass(repr=False, eq=False)
class Bytes(Content):
    MEDIA_TYPE_HINT: ClassVar[str] = 'application/octet-stream'
    data: bytes

@dataclass(repr=False, eq=False)
class Text(Content):
    MEDIA_TYPE_HINT: ClassVar[str] = 'text/plain'
    text: str

@dataclass(repr=False, eq=False)
class URLEncodedFormData(Content):
    MEDIA_TYPE_HINT: ClassVar[str] = 'application/x-www-form-urlencoded'
    data: Mapping[str, str]

@dataclass(repr=False, eq=False)
class JSON(Content):
    MEDIA_TYPE_HINT: ClassVar[str] = 'application/json'
    json: JSON_ro

@dataclass(repr=False, eq=False)
class MultipartFormData(Content):
    @dataclass(repr=False, eq=False)
    class Field:
        name: str

    @dataclass(repr=False, eq=False)
    class TextField(Field):
        text: str

    @dataclass(repr=False, eq=False)
    class FileField(Field):
        file: IO[bytes]
        filename: Optional[str] = None
        content_type: Optional[str] = 'application/octet-stream'

    MEDIA_TYPE_HINT: ClassVar[str] = 'multipart/form-data'
    parts: Sequence[Field]



def make_multipart_form_data_payload(files: RequestFiles) -> MultipartFormData:
    parts: list[MultipartFormData.Field] = []
    for key, value in files.items():
        field: MultipartFormData.Field
        if isinstance(value, str):
            field = MultipartFormData.TextField(key, value)
        else:
            field = MultipartFormData.FileField(key, value)
        parts.append(field)
    return MultipartFormData(parts)

def make_payload(
    data: Optional[Union[Mapping[str, str], bytes]] = None,
    json: JSON_ro = None,
    files: Optional[RequestFiles] = None,
) -> Optional[Payload]:
    if files is not None:
        if json is not None:
            raise TypeError("mutually exclusive parameters: `files`, `json`")
        if data is not None:
            if isinstance(data, bytes):
                raise TypeError("`data` cannot be bytes when `files` is used")
            files = {**data, **files}
        return make_multipart_form_data_payload(files)

    if data is not None:
        if json is not None:
            raise TypeError("mutually exclusive parameters: `data`, `json`")
        if isinstance(data, bytes):
            return Bytes(data)
        return URLEncodedFormData(data)

    if json is not None:
        return JSON(json)

    return None
