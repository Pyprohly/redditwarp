
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .image_size_named_tuple import ImageSize

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class ImageWidgetItem:
    url: str
    size: ImageSize
    link: str
