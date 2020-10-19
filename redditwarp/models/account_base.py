
from __future__ import annotations
from typing import Mapping, Any

from .original_reddit_thing_object import OriginalRedditThingObject

class MyAccountBase(OriginalRedditThingObject):
    class Subreddit:
        def __init__(self, outer: MyAccountBase, d: Mapping[str, Any]):
            self.name: str = d['display_name']
            #: One of `public`, `private`, `restricted`, `archived`,
            #: `employees_only`, `gold_only`, or `gold_restricted`.
            self.type: str = d['subreddit_type']
            self.subscriber_count: int = d['subscribers']
            self.title: str = d['title']
            self.summary_description: str = d['public_description']
            self.nsfw: bool = d['over_18']

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.name: str = d['name']
        self.has_mail: bool = d['has_mail']
        self.has_mod_mail: bool = d['has_mod_mail']
        self.inbox_count: int = d['inbox_count']
        self.coins: int = d['coins']
        self.friend_count: int = d['num_friends']
        self.is_suspended: bool = d['is_suspended']
        self.nsfw: bool = d['over_18']

        self.subreddit = self.Subreddit(self, d['subreddit'])
