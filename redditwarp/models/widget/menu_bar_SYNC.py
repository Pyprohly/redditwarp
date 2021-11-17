
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Any, Sequence
if TYPE_CHECKING:
    from .menu_bar import Tab

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class MenuBar:
    d: Mapping[str, Any]
    idt: str
    kind: str
    show_wiki: bool
    tabs: Sequence[Tab]
