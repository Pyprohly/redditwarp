
from __future__ import annotations
from typing import Mapping, Any, NamedTuple, Optional, Sequence

from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class WidgetImageUploadLease(IArtifact):
    d: Mapping[str, Any]
    endpoint: str
    fields: Mapping[str, str]
    s3_object_key: str
    location: str


class ImageSize(NamedTuple):
    width: int
    height: int

class ButtonWidgetNamespace:
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
        image_size: ImageSize


    @dataclass(repr=False, eq=False)
    class Button:
        label: str
        link: str
        hover_state: Optional[ButtonWidgetNamespace.HoverState]

    @dataclass(repr=False, eq=False)
    class TextButton(Button):
        text_color: str
        fill_color: str
        stroke_color: str

    @dataclass(repr=False, eq=False)
    class ImageButton(Button):
        image_url: str
        image_size: ImageSize

class ImageWidgetNamespace:
    @dataclass(repr=False, eq=False)
    class ImageWidgetItem:
        url: str
        size: ImageSize
        link: str

class CommunityListWidgetNamespace:
    @dataclass(repr=False, eq=False)
    class CommunityListWidgetItem:
        name: str
        subscribers: int
        icon_img: str
        community_icon: str
        primary_color: str
        nsfw: bool

class CalendarWidgetNamespace:
    @dataclass(repr=False, eq=False)
    class CalendarWidgetConfiguration:
        num_events: int
        show_title: bool
        show_description: bool
        show_location: bool
        show_date: bool
        show_time: bool

class PostFlairWidgetNamespace:
    @dataclass(repr=False, eq=False)
    class PostFlairWidgetItem:
        d: Mapping[str, Any]
        uuid: str
        type: str
        text: str
        bg_color: str
        fg_light_or_dark: str

class CustomCSSWidgetNamespace:
    @dataclass(repr=False, eq=False)
    class CustomCSSWidgetImageInfo:
        url: str
        width: Optional[int]
        height: Optional[int]
        name: str

class ModeratorListWidgetNamespace:
    @dataclass(repr=False, eq=False)
    class ModeratorInfo:
        name: str
        flair_type: str
        flair_text: str
        flair_fg_light_or_dark: str
        flair_bg_color: str
        flair_has_had_flair: bool

class RulesWidgetNamespace:
    @dataclass(repr=False, eq=False)
    class Rule:
        description: str
        description_html: str
        short_name: str
        violation_reason: str
        created_ut: int


class MenuBarNamespace:
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
        items: Sequence[MenuBarNamespace.SubmenuItem]
