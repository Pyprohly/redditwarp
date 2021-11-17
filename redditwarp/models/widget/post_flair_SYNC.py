
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .post_flair import PostFlairWidgetItem

from dataclasses import dataclass

from .widget_SYNC import Widget

@dataclass(repr=False, eq=False)
class PostFlairWidget(Widget):
    display: str
    order: Sequence[str]
    templates: Sequence[PostFlairWidgetItem]
