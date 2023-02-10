
from __future__ import annotations
from typing import Mapping, Any

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class PostFlairWidgetItem:
    d: Mapping[str, Any]
    uuid: str
    text_mode: str
    text: str
    bg_color: str
    fg_color_scheme: str
