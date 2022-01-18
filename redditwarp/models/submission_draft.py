
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime
from dataclasses import dataclass

from .artifact import IArtifact

@dataclass(repr=False, eq=False)
class Draft(IArtifact):
    @dataclass(repr=False, eq=False)
    class FlairInfo:
        uuid: str = ''
        type: str = ''
        text_override: str = ''
        bg_color: str = ''
        fg_light_or_dark: str = ''

    d: Mapping[str, Any]
    uuid: str
    created_at: datetime
    modified_at: datetime
    public: bool
    subreddit_id: Optional[int]
    title: str
    reply_notifications: bool
    spoiler: bool
    nsfw: bool
    original_content: bool
    flair: Optional[FlairInfo]

@dataclass(repr=False, eq=False)
class MarkdownDraft(Draft):
    body: str

@dataclass(repr=False, eq=False)
class RichTextDraft(Draft):
    pass
