
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .original_reddit_thing_object import OriginalRedditThingObject
from ..auth.const import AUTHORIZATION_BASE_URL

class CommentBase(OriginalRedditThingObject):
    class Author:
        def __init__(self, outer: CommentBase, d: Mapping[str, Any]):
            self.name: str = d['author']
            self.id36: str = d['author_fullname'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.has_premium: bool = d['author_premium']

    class Submission:
        def __init__(self, outer: CommentBase, d: Mapping[str, Any]):
            self.id36: str = d['link_id'].split('_', 1)[-1]
            self.id = int(self.id36, 36)

    class Subreddit:
        def __init__(self, outer: CommentBase, d: Mapping[str, Any]):
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.name: str = d['subreddit']
            #: One of `public`, `private`, `restricted`, `archived`,
            #: `employees_only`, `gold_only`, `gold_restricted`, `user`.
            self.type: str = d['subreddit_type']

    class Moderator:
        def __init__(self, outer: CommentBase, d: Mapping[str, Any]):
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

    THING_PREFIX = 't1'

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.body: str = d['body']
        self.body_html: str = d['body_html']
        #: Works even if score is hidden (`hide_score` JSON field is `True`).
        self.score: int = d['score']
        self.score_hidden: bool = d['score_hidden']

        self.rel_permalink: str = AUTHORIZATION_BASE_URL + d['permalink']
        self.permalink: str = d['permalink']

        a: Any = d['edited']
        self.edited = bool(a)
        self.edited_ut: Optional[int] = int(a) if self.edited else None
        self.edited_at: Optional[datetime] = None
        if self.edited_ut is not None:
            self.edited_at = datetime.fromtimestamp(self.edited_ut, timezone.utc)

        self.is_submitter: bool = d['is_submitter']
        self.stickied: bool = d['stickied']
        self.archived: bool = d['archived']
        self.locked: bool = d['locked']
        #: Whether the comment is collapsed by default, i.e., when it has been downvoted significantly.
        self.collapsed: bool = d['collapsed']

        _parent_id: str = d['parent_id']
        self.top_level: bool = _parent_id.startswith('t3_')
        self.parent_comment_id36: Optional[str] = None
        self.parent_comment_id: Optional[int] = None
        if _parent_id.startswith('t1_'):
            self.parent_comment_id36 = _parent_id.split('_', 1)[-1]
            self.parent_comment_id = int(self.parent_comment_id36, 36)

        # User context fields
        #: For clients with no user context this will always be `False`.
        self.saved: bool = d['saved']
        self.inbox_replies: bool = d['send_replies']

        self.submission = self.Submission(self, d)
        self.subreddit = self.Subreddit(self, d)

        self.author = None
        s: str = d['author']
        if not s.startswith('['):
            self.author = self.Author(self, d)

        self.mod = None
        # `spam`, `ignore_reports`, `approved`, `removed`, and `rte_mode`
        # are all fields that aren't available when the current user is
        # not a moderator of the subreddit (or there’s no user context).
        if 'spam' in d:
            self.mod = self.Moderator(self, d)


class LooseCommentBase(CommentBase):
    # For comments originating from `/comments` or `/r/{subreddit}/comments`.

    class Submission(CommentBase.Submission):
        def __init__(self, outer: LooseCommentBase, d: Mapping[str, Any]):
            super().__init__(outer, d)
            self.comment_count: int = d['num_comments']
            self.nsfw: bool = d['over_18']
            self.title: str = d['link_title']
            self.author_name: str = d['link_author']
            self.permalink: str = d['permalink']

    class Subreddit(CommentBase.Subreddit):
        def __init__(self, outer: LooseCommentBase, d: Mapping[str, Any]):
            super().__init__(outer, d)
            self.quarantined: bool = d['quarantine']

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
