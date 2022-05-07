
from __future__ import annotations
from typing import Mapping, Any

class UserSummary:
    def __init__(self, d: Mapping[str, Any], id36: str):
        self.d: Mapping[str, Any] = d
        self.id36: str = id36
        self.id: int = int(id36, 36)
        self.name: str = d['name']
        self.created_ut: int = int(d['created_utc'])
        self.submission_karma: int = d['link_karma']
        self.comment_karma: int = d['comment_karma']
        self.profile_img: str = d['profile_img']
        self.profile_color: str = d['profile_color']
        self.nsfw: bool = d['profile_over_18']
