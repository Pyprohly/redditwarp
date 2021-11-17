
from __future__ import annotations
from typing import Optional

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class CustomCSSWidgetImageInfo:
    url: str
    width: Optional[int]
    height: Optional[int]
    name: str
