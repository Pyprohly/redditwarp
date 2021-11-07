
from __future__ import annotations
from typing import Optional

from dataclasses import dataclass

@dataclass(repr=False, eq=False)
class HoverState:
    pass

@dataclass(repr=False, eq=False)
class TextHoverState(HoverState):
    label: str
    text_color: str
    fill_color: str
    stroke_color: str

@dataclass(repr=False, eq=False)
class ImageHoverState(HoverState):
    image_url: str
    image_size: tuple[int, int]


@dataclass(repr=False, eq=False)
class Button:
    label: str
    link: str
    hover_state: Optional[HoverState]

@dataclass(repr=False, eq=False)
class TextButton(Button):
    text_color: str
    fill_color: str
    stroke_color: str

@dataclass(repr=False, eq=False)
class ImageButton(Button):
    image_url: str
    image_size: tuple[int, int]
