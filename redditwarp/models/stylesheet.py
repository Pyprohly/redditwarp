
from __future__ import annotations
from typing import Sequence

from dataclasses import dataclass

@dataclass
class StylesheetImage:
    url: str
    name: str

@dataclass(repr=False, eq=False)
class StylesheetInfo:
    content: str
    images: Sequence[StylesheetImage]
