
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .datamemento import DatamementoPropertiesMixin

class ModeratedSubreddit(DatamementoPropertiesMixin):
    class Me:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.is_subscribed: bool = d['user_is_subscriber']
            ("")

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        full_id36: str = d['name']
        self.id36: str = full_id36[3:]
        ("""
            The ID of the subreddit as a base 36 number.
            """)
        self.id: int = int(self.id36, 36)
        ("""
            The subreddit ID.
            """)
        self.name: str = d['display_name']
        ("""
            The name of the subreddit.
            """)
        self.openness: str = d['subreddit_type']
        ("""
            Either: `public`, `private`, `restricted`, `archived`,
            `employees_only`, `gold_only`, `gold_restricted`, or `user`.
            """)
        self.created_ut: int = -1
        ("""
            If a normal subreddit, the unix timestamp of when the subreddit was created.

            If a user subreddit, the value is `-1`.

            Use `self.openness == 'user'` to tell if a subreddit is a user subreddit.
            """)
        self.created_at: datetime = datetime.min
        ("""
            If a normal subreddit, a datetime object of when the subreddit was created.

            If a user subreddit, the value is `datetime.min`.

            Use `self.openness == 'user'` to tell if a subreddit is a user subreddit.
            """)
        if self.openness != 'user':
            self.created_ut = int(d['created_utc'])
            self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)

        self.title: str = d['title']
        ("")
        self.subscriber_count: int = d['subscribers']
        ("")
        self.nsfw: bool = d['over_18']
        ("")
        self.icon_img: str = d['icon_img']
        ("")

        self.me: Optional[ModeratedSubreddit.Me] = None
        ("")
        if 'user_is_subscriber' in d:
            self.me = self.Me(d)
