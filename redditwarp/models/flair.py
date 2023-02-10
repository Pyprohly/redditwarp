
from typing import Any, Mapping, Optional, Sequence

from dataclasses import dataclass

from .artifact import IArtifact


@dataclass(repr=False, eq=False)
class FlairTemplate(IArtifact):
    d: Mapping[str, Any]
    uuid: str
    text_mode: str
    ("""
        Either `text` or `richtext`.
        """)
    text: str
    css_class: str
    bg_color: str
    ("""
        A background color hex string. E.g., `#46d160`.

        If a user flair template and the background color is unset then
        the value is an empty string. The value cannot be empty for
        post flair templates.
        """)
    fg_color_scheme: str
    ("""
        Either `dark` or `light`.
        """)
    mod_only: bool
    ("""
        Whether flair is only available for mods to select.
        """)
    user_editable: bool
    ("""
        Whether users are able to edit the flair text.
        """)
    allowable_content: str
    ("""
        Either: `all`, `emoji`, `text`.

        Value `all` if both text and emojis are allowed in the flair text,
        `emoji` if only emojis are allowed, `text` if only text is allowed.
        """)
    max_emojis: int
    ("""
        Maximum number of emojis allowed in a flair.

        An integer from 1 to 10.
        """)


@dataclass(repr=False, eq=False)
class CurrentFlairChoice:
    template_uuid: Optional[str]
    ("""
        Value is null if no flair template is being used.
        """)
    text: str
    css_class: str

@dataclass(repr=False, eq=False)
class FlairTemplateChoice:
    uuid: str
    text: str
    css_class: str
    user_editable: bool

@dataclass(repr=False, eq=False)
class FlairChoices:
    current: Optional[CurrentFlairChoice]
    choices: Sequence[FlairTemplateChoice]
    subreddit_user_flair_position: str
    ("""
        Either: `left`, `right`, or empty string.
        """)


@dataclass(repr=False, eq=False)
class UserFlairAssociation:
    user: str
    text: str
    css_class: str
    has_had_flair_css_class_assigned_before_in_subreddit_when_no_flair_template_assigned: bool
