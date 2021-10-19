
from typing import Any, Mapping, Optional, NamedTuple, Sequence

import sys
from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class FlairTemplate(IArtifact):
    d: Mapping[str, Any]
    uuid: str
    type: str
    mod_only: bool
    text: str
    bg_color: str
    fg_light_or_dark: str
    allowable_content: str
    css_class: str
    max_emojis: int
    text_editable: bool

    if sys.version_info[:3] == (3, 9, 7):
        # https://bugs.python.org/issue45081
        def __init__(self,
            d: Mapping[str, Any],
            uuid: str,
            type: str,
            mod_only: bool,
            text: str,
            bg_color: str,
            fg_light_or_dark: str,
            allowable_content: str,
            css_class: str,
            max_emojis: int,
            text_editable: bool,
        ) -> None:
            self.d = d
            self.uuid = uuid
            self.type = type
            self.mod_only = mod_only
            self.text = text
            self.bg_color = bg_color
            self.fg_light_or_dark = fg_light_or_dark
            self.allowable_content = allowable_content
            self.css_class = css_class
            self.max_emojis = max_emojis
            self.text_editable = text_editable

@dataclass(repr=False, eq=False)
class CurrentFlairChoice:
    uuid: Optional[str]
    text: str
    css_class: str
    position: str

@dataclass(repr=False, eq=False)
class FlairTemplateChoice:
    uuid: str
    text: str
    css_class: str
    position: str
    text_editable: bool

class FlairChoices(NamedTuple):
    current: Optional[CurrentFlairChoice]
    choices: Sequence[FlairTemplateChoice]

@dataclass(repr=False, eq=False)
class UserFlairAssociation:
    username: str
    text: str
    has_had_css_class_when_no_flair_template: bool
    css_class: str
