
from __future__ import annotations
from typing import Mapping, Any, Sequence

from dataclasses import dataclass
from datetime import datetime, timezone

from .artifact import IArtifact


# WikiPageRevisionAuthorUser is pretty much the same as User except the
# `awardee_karma`, `awarder_karma`, `total_karma` fields are missing.

class WikiPageRevisionAuthorUser(IArtifact):
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

        self.has_premium: bool = d['is_gold']
        self.has_verified_email: bool = d['has_verified_email']

        self.is_admin: bool = d['is_employee']
        self.is_a_subreddit_moderator: bool = d['is_mod']

        self.icon_img: str = d['icon_img']

        self.subreddit: WikiPageRevisionAuthorUser.Subreddit = self.Subreddit(d)
        self.me: WikiPageRevisionAuthorUser.Me = self.Me(d)


@dataclass(repr=False, eq=False, frozen=True)
class WikiPage(IArtifact):
    d: Mapping[str, Any]
    body: str
    body_html: str
    can_revise: bool
    revision_uuid: str
    revision_unixtime: int
    revision_author: WikiPageRevisionAuthorUser
    revision_message: str

@dataclass(repr=False, eq=False, frozen=True)
class WikiPageRevision(IArtifact):
    d: Mapping[str, Any]
    uuid: str
    unixtime: int
    author: WikiPageRevisionAuthorUser
    message: str
    hidden: bool

@dataclass(repr=False, eq=False, frozen=True)
class WikiPageSettings:
    permlevel: int
    editors: Sequence[WikiPageRevisionAuthorUser]
    unlisted: bool
