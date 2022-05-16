
from __future__ import annotations
from typing import Mapping, Any, Sequence, TypeVar, Generic

from dataclasses import dataclass
from functools import cached_property
from datetime import datetime, timezone

from .artifact import IArtifact, Artifact


# WikiPageRevisionAuthorUser is pretty much the same as User except the
# `awardee_karma`, `awarder_karma`, `total_karma` fields are missing.

class BaseWikiPageRevisionAuthorUser(Artifact):
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

        self.has_premium: bool = d['is_gold']

        self.is_admin: bool = d['is_employee']
        self.is_friend: bool = d['is_friend']
        self.is_a_subreddit_moderator: bool = d['is_mod']

        self.icon_img: str = d['icon_img']

        self.subreddit: BaseWikiPageRevisionAuthorUser.Subreddit = self.Subreddit(d['subreddit'])



TWikiPageRevisionAuthorUser = TypeVar('TWikiPageRevisionAuthorUser', bound=BaseWikiPageRevisionAuthorUser)

@dataclass(repr=False, eq=False)
class GBaseWikiPage(IArtifact, Generic[TWikiPageRevisionAuthorUser]):
    d: Mapping[str, Any]
    body: str
    body_html: str
    can_revise: bool
    revision_uuid: str
    revision_timestamp: int
    revision_author: TWikiPageRevisionAuthorUser
    revision_message: str

    @cached_property
    def revision_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.revision_timestamp, timezone.utc)

@dataclass(repr=False, eq=False)
class BaseWikiPage(GBaseWikiPage[BaseWikiPageRevisionAuthorUser]):
    pass


@dataclass(repr=False, eq=False)
class GBaseWikiPageRevision(IArtifact, Generic[TWikiPageRevisionAuthorUser]):
    d: Mapping[str, Any]
    uuid: str
    timestamp: int
    author: TWikiPageRevisionAuthorUser
    message: str
    hidden: bool

@dataclass(repr=False, eq=False)
class BaseWikiPageRevision(GBaseWikiPageRevision[BaseWikiPageRevisionAuthorUser]):
    pass


@dataclass(repr=False, eq=False)
class GBaseWikiPageSettings(Generic[TWikiPageRevisionAuthorUser]):
    permlevel: int
    editors: Sequence[TWikiPageRevisionAuthorUser]
    unlisted: bool

@dataclass(repr=False, eq=False)
class BaseWikiPageSettings(GBaseWikiPageSettings[BaseWikiPageRevisionAuthorUser]):
    pass
