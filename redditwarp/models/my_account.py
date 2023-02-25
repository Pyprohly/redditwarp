
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

from .datamemento import DatamementoBase

class MyAccount(DatamementoBase):
    class Subreddit:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.name: str = d['display_name']
            ("")
            self.openness: str = d['subreddit_type']
            ("""
                Either: `public`, `private`, `restricted`, `archived`,
                `employees_only`, `gold_only`, `gold_restricted`, or `user`.
                """)
            self.subscriber_count: int = d['subscribers']
            ("")
            self.title: str = d['title']
            ("")
            self.public_description: str = d['public_description']
            ("")
            self.nsfw: bool = d['over_18']
            ("")

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.id36: str = d['id']
        ("""
            User ID of the current user account as a base 36 number.
            """)
        self.id: int = int(self.id36, 36)
        ("""
            User ID of the current user account.
            """)
        self.name: str = d['name']
        ("""
            Username of the current user account.
            """)
        self.created_ut: int = int(d['created_utc'])
        ("""
            Unix timestamp of when the current user account was created.
            """)
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("""
            Datetime object of when the current user account was created.
            """)
        self.post_karma: int = d['link_karma']
        ("")
        self.comment_karma: int = d['comment_karma']
        ("")
        self.awardee_karma: int = d['awardee_karma']
        ("")
        self.awarder_karma: int = d['awarder_karma']
        ("")
        self.total_karma: int = d['total_karma']
        ("")
        self.has_mail: bool = d['has_mail']
        ("""
            True if the current user has a new inbox message.
            """)
        self.has_mod_mail: bool = d['has_mod_mail']
        ("""
            True if the current user has a new modmail message.
            """)
        self.inbox_count: int = d['inbox_count']
        ("""
            Number of new inbox messages.
            """)
        self.coins: int = d['coins']
        ("""
            How rich the current user is.
            """)
        self.friend_count: int = d['num_friends']
        ("""
            Number of friends in the current user's friends list.

            This is an old reddit feature. See `<https://www.reddit.com/prefs/friends/>`_.
            """)
        self.nsfw: bool = d['over_18']
        ("""
            Whether the current user account has opted in to NSFW content.

            On old reddit, this is the preference option that says
            "I am over eighteen years old and willing to view adult content".
            """)

        self.subreddit: MyAccount.Subreddit = self.Subreddit(d['subreddit'])
        ("""
            Information about the current user account's user subreddit.
            """)
