
from __future__ import annotations
from typing import Mapping, Any, Sequence

from dataclasses import dataclass
from datetime import datetime, timezone

from .datamemento import DatamementoPropertiesMixin, DatamementoDataclassesMixin


class WikiPageRevisionAuthorUser(DatamementoPropertiesMixin):
    """
    This class is pretty much the same as :class:`~.models.User` except
    the `awardee_karma`, `awarder_karma`, `total_karma` fields are missing.
    """
    class Subreddit:
        def __init__(self, d: Mapping[str, Any]) -> None:
            d = d['subreddit']
            self.name: str = d['display_name']
            ("")
            self.openness: str = d['subreddit_type']
            ("")
            self.subscriber_count: int = d['subscribers']
            ("")
            self.title: str = d['title']
            ("")
            self.public_description: str = d['public_description']
            ("")
            self.nsfw: bool = d['over_18']
            ("")

    class Me:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.is_friend: bool = d['is_friend']
            ("")
            self.is_blocked: bool = d['is_blocked']
            ("")

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.id36: str = d['id']
        ("")
        self.idn: int = int(self.id36, 36)
        ("")
        self.id: int = self.idn
        ("")
        self.name: str = d['name']
        ("")
        self.created_ut: int = int(d['created_utc'])
        ("")
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("")

        self.post_karma: int = d['link_karma']
        ("")
        self.comment_karma: int = d['comment_karma']
        ("")

        self.has_premium: bool = d['is_gold']
        ("")
        self.has_verified_email: bool = d['has_verified_email']
        ("")

        self.is_admin: bool = d['is_employee']
        ("")
        self.is_a_subreddit_moderator: bool = d['is_mod']
        ("")

        self.icon_img: str = d['icon_img']
        ("")

        self.subreddit: WikiPageRevisionAuthorUser.Subreddit = self.Subreddit(d)
        ("")
        self.me: WikiPageRevisionAuthorUser.Me = self.Me(d)
        ("")


@dataclass(repr=False, eq=False, frozen=True)
class WikiPage(DatamementoDataclassesMixin):
    d: Mapping[str, Any]
    body: str
    ("""
        The wiki page markdown content.
        """)
    body_html: str
    ("""
        The wiki page content as HTML.
        """)
    can_revise: bool
    ("""
        True if the current user may edit the wiki page.
        """)
    revision_uuid: str
    ("""
        The current revision UUID.
        """)
    revision_unixtime: int
    ("""
        UNIX timestamp of when the current revision was commited.
        """)
    revision_author: WikiPageRevisionAuthorUser
    ("""
        Author of the revision.
        """)
    revision_message: str
    ("""
        The current revision message.

        Up to 256 characters long.
        """)

@dataclass(repr=False, eq=False, frozen=True)
class WikiPageRevision(DatamementoDataclassesMixin):
    d: Mapping[str, Any]
    uuid: str
    ("""
        Revision UUID.
        """)
    unixtime: int
    ("""
        UNIX timestamp of when the current revision was commited.
        """)
    author: WikiPageRevisionAuthorUser
    ("""
        Author of the revision.
        """)
    message: str
    ("""
        Revision message.

        Up to 256 characters long.
        """)
    hidden: bool
    ("""
        True if the revision is hidden.
        """)

@dataclass(repr=False, eq=False, frozen=True)
class WikiPageSettings:
    permlevel: int
    ("""
        Permission level indicating who can edit this wiki page.

        "who can edit this page?"

        `0`: "use subreddit wiki permissions"
        `1`: "only approved wiki contributors for this page may edit"
        `2`: "only mods may edit and view"
        """)
    editors: Sequence[WikiPageRevisionAuthorUser]
    ("""
        List of users allowed to edit this page.
        """)
    indexed: bool
    ("""
        Whether this wiki page is indexed on the wiki page list.
        """)
