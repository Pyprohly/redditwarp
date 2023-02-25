
from __future__ import annotations
from typing import Any, Mapping, Sequence, Iterator, Union, overload

from dataclasses import dataclass

from .datamemento import DatamementoDataclassesMixin


@dataclass(repr=False, eq=False)
class FlairTemplate(DatamementoDataclassesMixin):
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
    text_editable: bool
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
class FlairTemplateChoice:
    uuid: str
    text: str
    css_class: str
    text_editable: bool

@dataclass(repr=False, eq=False)
class FlairTemplateChoices(Sequence[FlairTemplateChoice]):
    choices: Sequence[FlairTemplateChoice]
    subreddit_flair_user_position: str
    ("""
        Either: `left`, `right`, or empty string.
        """)

    def __len__(self) -> int:
        return len(self.choices)

    def __contains__(self, item: object) -> bool:
        return item in self.choices

    def __iter__(self) -> Iterator[FlairTemplateChoice]:
        return iter(self.choices)

    @overload
    def __getitem__(self, index: int) -> FlairTemplateChoice: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[FlairTemplateChoice]: ...
    def __getitem__(self, index: Union[int, slice]) -> Union[FlairTemplateChoice, Sequence[FlairTemplateChoice]]:
        return self.choices[index]


@dataclass(repr=False, eq=False)
class UserFlairAssociation:
    user: str
    text: str
    css_class: str
    has_had_flair_css_class_assigned_before_in_subreddit_when_no_flair_template_assigned: bool
