
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .button import Button

from dataclasses import dataclass

from .widget_ASYNC import Widget

@dataclass(repr=False, eq=False)
class ButtonWidget(Widget):
    description: str
    description_html: str
    buttons: Sequence[Button]
