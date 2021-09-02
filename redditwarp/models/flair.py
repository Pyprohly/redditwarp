
from typing import Any, Mapping, Optional, NamedTuple, Sequence

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
