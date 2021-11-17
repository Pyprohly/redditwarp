
from __future__ import annotations

from dataclasses import dataclass

from .widget_ASYNC import Widget

@dataclass(repr=False, eq=False)
class TextAreaWidget(Widget):
    text: str
    text_html: str
