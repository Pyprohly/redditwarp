
from __future__ import annotations
from typing import Mapping, Any, Optional

import sys
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

    if sys.version_info[:3] == (3, 9, 7):
        # https://bugs.python.org/issue45081
        def __init__(self,
            d: Mapping[str, Any],
            uuid: str,
            created_at: datetime,
            modified_at: datetime,
            public: bool,
            subreddit_id: Optional[int],
            title: str,
            reply_notifications: bool,
            spoiler: bool,
            nsfw: bool,
            original_content: bool,
            flair: Optional[FlairInfo],
        ) -> None:
            self.d = d
            self.uuid = uuid
            self.created_at = created_at
            self.modified_at = modified_at
            self.public = public
            self.subreddit_id = subreddit_id
            self.title = title
            self.reply_notifications = reply_notifications
            self.spoiler = spoiler
            self.nsfw = nsfw
            self.original_content = original_content
            self.flair = flair

@dataclass(repr=False, eq=False)
class MarkdownDraft(Draft):
    body: str

@dataclass(repr=False, eq=False)
class RichTextDraft(Draft):
    pass
