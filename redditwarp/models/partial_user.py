
from __future__ import annotations
from typing import Mapping, Any

class PartialUser:
    def __init__(self, d: Mapping[str, Any], id36: str):
        self.d = d
        self.id36 = id36
        self.id = int(id36, 36)
        self.name: str = d['name']
        self.created_ut = int(d['created_utc'])
        self.link_karma: int = d['link_karma']
        self.comment_karma: int = d['comment_karma']
        self.profile_img: str = d['profile_img']
        self.profile_color: str = d['profile_color']
        self.nsfw: bool = d['profile_over_18']
