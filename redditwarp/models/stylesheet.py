
from __future__ import annotations
from typing import Sequence

from dataclasses import dataclass

@dataclass
class StylesheetImage:
    name: str
    url: str

@dataclass(repr=False, eq=False)
class StylesheetInfo:
    content: str
    ("""
        The CSS content.
        """)
    images: Sequence[StylesheetImage]
