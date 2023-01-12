
from __future__ import annotations
import mimetypes

def guess_filename_mimetype(filename: str) -> str:
    y = mimetypes.guess_type(filename, strict=False)[0]
    return y or 'application/octet-stream'
