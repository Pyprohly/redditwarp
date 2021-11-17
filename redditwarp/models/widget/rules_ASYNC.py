
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
if TYPE_CHECKING:
    from .rules import Rule

from dataclasses import dataclass

from .widget_ASYNC import Widget

@dataclass(repr=False, eq=False)
class RulesWidget(Widget):
    display: str
    rules: Sequence[Rule]
