
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from .custom_css import CustomCSSWidgetImageInfo

from dataclasses import dataclass

from .widget_SYNC import Widget

@dataclass(repr=False, eq=False)
class CustomCSSWidget(Widget):
    text: str
    css: str
    height: Optional[int]
    image_data: Sequence[CustomCSSWidgetImageInfo]
