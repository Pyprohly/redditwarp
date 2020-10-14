
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .original_reddit_thing_object import OriginalRedditThingObject
from ..auth.const import AUTHORIZATION_BASE_URL

class SubmissionBase(OriginalRedditThingObject):
    class Author:
        def __init__(self, outer: SubmissionBase, d: Mapping[str, Any]):
            self.name: str = d['author']
            self.id36: str = d['author_fullname'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.has_premium: bool = d['author_premium']

    class Subreddit:
        def __init__(self, outer: SubmissionBase, d: Mapping[str, Any]):
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.name: str = d['subreddit']
            #: One of `public`, `private`, `restricted`, `archived`,
            #: `employees_only`, `gold_only`, or `gold_restricted`.
            self.type: str = d['subreddit_type']
            self.quarantined: bool = d['quarantine']
            self.subscriber_count: int = d['subreddit_subscribers']

    class Moderator:
        def __init__(self, outer: SubmissionBase, d: Mapping[str, Any]):
            self.spam: bool = d['spam']

            self.approved: bool = d['approved']
            self.approved_by: Optional[str] = d['approved_by']
            self.approved_ut: Optional[int] = d['approved_at_utc']
            self.approved_at: Optional[datetime] = None
            if self.approved_ut is not None:
                self.approved_at = datetime.fromtimestamp(self.approved_ut, timezone.utc)

            self.removed: bool = d['removed']
            self.removed_by: Optional[str] = d['removed_by']
            self.removed_ut: Optional[int] = d['removed_at_utc']
            self.removed_at: Optional[datetime] = None
            if self.removed_ut is not None:
                self.removed_at = datetime.fromtimestamp(self.removed_ut, timezone.utc)

    THING_PREFIX = 't3'

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.title: str = d['title']
        #: Works even if score is hidden (`hide_score` JSON field is `True`).
        self.score: int = d['score']
        self.score_hidden: bool = d['hide_score']
        self.comment_count: int = d['num_comments']

        self.rel_permalink: str = d['permalink']
        self.permalink: str = AUTHORIZATION_BASE_URL + d['permalink']

        a: Any = d['edited']
        self.edited = bool(a)
        self.edited_ut: Optional[int] = int(a) if self.edited else None
        self.edited_at: Optional[datetime] = None
        if self.edited_ut is not None:
            self.edited_at = datetime.fromtimestamp(self.edited_ut, timezone.utc)

        self.upvote_ratio: float = d['upvote_ratio']
        self.removal_category: Optional[str] = d['removed_by_category']
        #: One of None, `confidence` (best), `top`, `new`, `controversial`, `old`, `qa`.
        self.suggested_sort: Optional[str] = d['suggested_sort']
        self.stickied: bool = d['stickied']
        self.archived: bool = d['archived']
        self.locked: bool = d['locked']
        self.in_contest_mode: bool = d['contest_mode']
        self.nsfw: bool = d['over_18']
        self.crosspostable: bool = d['is_crosspostable']
        self.is_original_content: bool = d['is_original_content']
        self.robot_indexable: bool = d['is_robot_indexable']
        self.pinned: bool = d['pinned']

        # User context fields
        #: For clients with no user context this will always be `False`.
        self.saved: bool = d['saved']
        self.hidden: bool = d['hidden']
        self.inbox_replies: bool = d['send_replies']

        self.subreddit = self.Subreddit(self, d)

        s: str = d['author']
        self.author_name = s
        self.author = None
        if not s.startswith('['):
            self.author = self.Author(self, d)

        self.mod = None
        # `spam`, `ignore_reports`, `approved`, `removed`, and `rte_mode`
        # are all fields that aren't available when the current user is
        # not a moderator of the subreddit (or there’s no user context).
        if 'spam' in d:
            self.mod = self.Moderator(self, d)


class TextPostBase(SubmissionBase):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.body: str = d['selftext']
        self.body_html: str = d['selftext_html']

class LinkPostBase(SubmissionBase):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.link_url: str = d['url_overridden_by_dest']
