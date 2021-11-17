
from __future__ import annotations
from typing import Mapping, Any

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class PostFlairWidgetItem:
    d: Mapping[str, Any]
    uuid: str
    type: str
    text: str
    bg_color: str
    fg_light_or_dark: str
