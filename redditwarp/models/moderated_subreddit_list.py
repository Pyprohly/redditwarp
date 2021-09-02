
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .artifact import Artifact

class ModeratedSubredditListItem(Artifact):
    class Me:
        def __init__(self, d: Mapping[str, Any]):
            self.is_subscribed: bool = d['user_is_subscriber']

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        full_id36: str = d['name']
        self.id36: str = full_id36[3:]
        self.id = int(self.id36, 36)
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.name: str = d['display_name']
        self.type: str = d['subreddit_type']
        self.subscriber_count: int = d['subscribers']
        self.title: str = d['title']
        self.nsfw: bool = d['over_18']
        self.icon_img: str = d['icon_img']

        self.me = None
        if 'user_is_subscriber' in d:
            self.me = self.Me(d)
