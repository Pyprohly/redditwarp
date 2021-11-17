
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .image import ImageWidgetItem

from dataclasses import dataclass

from .widget_ASYNC import Widget

@dataclass(repr=False, eq=False)
class ImageWidget(Widget):
    items: Sequence[ImageWidgetItem]
