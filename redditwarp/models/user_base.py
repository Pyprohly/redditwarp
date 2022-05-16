
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .artifact import Artifact

class BaseUser(Artifact):
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

        self.submission_karma: int = d['link_karma']
        self.comment_karma: int = d['comment_karma']
        self.awardee_karma: int = d.get('awardee_karma', -1)
        self.awarder_karma: int = d.get('awarder_karma', -1)
        self.total_karma: int = d.get('total_karma', -1)

        self.has_premium: bool = d['is_gold']
        self.has_verified_email: bool = d['has_verified_email']

        self.is_admin: bool = d['is_employee']
        self.is_friend: bool = d['is_friend']
        self.is_a_subreddit_moderator: bool = d['is_mod']

        self.icon_img: str = d['icon_img']

        self.subreddit: BaseUser.Subreddit = self.Subreddit(d['subreddit'])
