
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .artifact import Artifact

class MyAccount(Artifact):
    class Subreddit:
        def __init__(self, d: Mapping[str, Any]):
            self.name: str = d['display_name']
            self.openness: str = d['subreddit_type']
            self.subscriber_count: int = d['subscribers']
            self.title: str = d['title']
            self.public_description: str = d['public_description']
            self.nsfw: bool = d['over_18']

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.name: str = d['name']
        self.has_mail: bool = d['has_mail']
        self.has_mod_mail: bool = d['has_mod_mail']
        self.inbox_count: int = d['inbox_count']
        self.coins: int = d['coins']
        self.friend_count: int = d['num_friends']
        self.is_suspended: bool = d['is_suspended']
        self.nsfw: bool = d['over_18']

        self.subreddit: MyAccount.Subreddit = self.Subreddit(d['subreddit'])
