
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .artifact import IArtifact

class User(IArtifact):
    class Subreddit:
        def __init__(self, d: Mapping[str, Any]) -> None:
            d = d['subreddit']
            self.name: str = d['display_name']
            self.openness: str = d['subreddit_type']
            self.subscriber_count: int = d['subscribers']
            self.title: str = d['title']
            self.public_description: str = d['public_description']
            self.nsfw: bool = d['over_18']

    class Me:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.is_friend: bool = d['is_friend']
            self.is_blocked: bool = d['is_blocked']

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.name: str = d['name']

        self.post_karma: int = d['link_karma']
        self.comment_karma: int = d['comment_karma']
        # The user objects from wiki related data don't have these fields
        # but it uses a different user class type for now.
        self.awardee_karma: int = d.get('awardee_karma', 0)
        self.awarder_karma: int = d.get('awarder_karma', 0)
        self.total_karma: int = d.get('total_karma', 0)

        self.has_premium: bool = d['is_gold']
        self.has_verified_email: bool = d['has_verified_email']

        self.is_admin: bool = d['is_employee']
        self.is_a_subreddit_moderator: bool = d['is_mod']

        self.icon_img: str = d['icon_img']

        self.subreddit: User.Subreddit = self.Subreddit(d)
        self.me: User.Me = self.Me(d)


class SuspendedUser(IArtifact):
    class Me:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.is_blocked: bool = d['is_blocked']

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.name: str = d['name']
        self.awardee_karma: int = d['awardee_karma']
        self.awarder_karma: int = d['awarder_karma']
        self.total_karma: int = d['total_karma']

        self.me: SuspendedUser.Me = self.Me(d)
