
from __future__ import annotations
from typing import Mapping, Any

from .original_reddit_thing_object import OriginalRedditThingObject

class UserBase(OriginalRedditThingObject):
    THING_PREFIX = 't2'

    class Subreddit:
        def __init__(self, outer: UserBase, d: Mapping[str, Any]):
            self.name: str = d['display_name']
            self.subscriber_count: int = d['subscribers']
            self.title: str = d['title']
            self.summary_description: str = d['public_description']
            self.summary_description_html: str = d['public_description_html']
            self.nsfw: bool = d['over18']

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.name: str = d['name']

        #: One of `public`, `private`, `restricted`, `archived`,
        #: `employees_only`, `gold_only`, or `gold_restricted`.
        self.type: str = d['subreddit_type']

        #: Karma accumulated from posting.
        self.link_karma: int = d['link_karma']
        #: Karma accumulated from commenting.
        self.comment_karma: int = d['comment_karma']
        #: Karma accumulated for being awarded.
        self.awardee_karma: int = d['awardee_karma']
        #: Karma accumulated for giving awards.
        self.awarder_karma: int = d['awarder_karma']
        #: Same as `link_karma`, `comment_karma`, `awardee_karma`, and `awarder_karma` added.
        self.total_karma: int = d['total_karma']

        self.has_premium: bool = d['is_gold']

        #: Is a Reddit admin.
        self.is_employee: bool = d['is_employee']
        #: Whether the user is a friend of the current user.
        self.is_friend: bool = d['is_friend']
        #: Is a moderator of any subreddit.
        self.subreddit_moderator: bool = d['is_mod']

        self.icon_img: str = d['icon_img']

        self.subreddit = self.Subreddit(self, d)
