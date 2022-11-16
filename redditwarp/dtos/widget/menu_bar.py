
from __future__ import annotations
from typing import Sequence

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class Tab:
    label: str

@dataclass(repr=False, eq=False)
class LinkTab(Tab):
    link: str


@dataclass(repr=False, eq=False)
class SubmenuItem:
    label: str
    link: str

@dataclass(repr=False, eq=False)
class SubmenuTab(Tab):
    items: Sequence[SubmenuItem]
