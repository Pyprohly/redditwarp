
from __future__ import annotations

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class ImageInfo:
    url: str
    size: tuple[int, int]
    link: str
