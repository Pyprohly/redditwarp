
from __future__ import annotations
from typing import Mapping, Any

class UserSummary:
    def __init__(self, d: Mapping[str, Any], id36: str) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.id36: str = id36
        ("""
            ID of the user account as a base 36 number.
            """)
        self.id: int = int(id36, 36)
        ("""
            ID of the user account.
            """)
        self.name: str = d['name']
        ("""
            Name of the user.
            """)
        self.created_ut: int = int(d['created_utc'])
        ("""
            Unix timestamp of when the user account was created.
            """)
        self.post_karma: int = d['link_karma']
        ("")
        self.comment_karma: int = d['comment_karma']
        ("")
        self.profile_img: str = d['profile_img']
        ("")
        self.profile_color: str = d['profile_color']
        ("")
        self.subreddit_nsfw: bool = d['profile_over_18']
        ("""
            Whether the user's user subreddit is NSFW.
            """)
