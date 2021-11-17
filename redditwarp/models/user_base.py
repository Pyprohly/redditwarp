
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .artifact import Artifact

class BaseUser(Artifact):
    class Subreddit:
        def __init__(self, d: Mapping[str, Any]):
            self.name: str = d['display_name']
            self.type: str = d['subreddit_type']
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

        #: Karma accumulated from posting.
        self.submission_karma: int = d['link_karma']
        #: Karma accumulated from commenting.
        self.comment_karma: int = d['comment_karma']
        #: Karma accumulated for being awarded.
        self.awardee_karma: int = d['awardee_karma']
        #: Karma accumulated for giving awards.
        self.awarder_karma: int = d['awarder_karma']
        #: Same as `link_karma`, `comment_karma`, `awardee_karma`, and `awarder_karma` added.
        self.total_karma: int = d['total_karma']

        self.has_premium: bool = d['is_gold']
        self.has_verified_email: bool = d['has_verified_email']

        #: Whether the user is a friend of the current user.
        self.is_friend: bool = d['is_friend']
        #: Is a moderator of any subreddit.
        self.is_a_subreddit_moderator: bool = d['is_mod']

        self.icon_img: str = d['icon_img']

        self.subreddit: BaseUser.Subreddit = self.Subreddit(d['subreddit'])
