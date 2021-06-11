
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .original_reddit_thing_object import OriginalRedditThingObject
from ..auth.const import AUTHORIZATION_BASE_URL

class CommentBase(OriginalRedditThingObject):
    class User:
        def __init__(self, d: Mapping[str, Any]):
            # User context fields
            self.saved: bool = d['saved']  # False if no user context
            self.reply_notifications: bool = d['send_replies']  # False if no user context
            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]  # None if no user context

    class Author:
        class AuthorFlair:
            def __init__(self, d: Mapping[str, Any]):
                self.has_had_flair: bool = d['author_flair_text'] is not None
                self.bg_color: str = d['author_flair_background_color'] or ''
                _author_flair_css_class_temp: Optional[str] = d['author_flair_css_class']
                self.has_had_css_class_when_no_flair_template: bool = _author_flair_css_class_temp is not None
                self.css_class: str = _author_flair_css_class_temp or ''
                self.template_uuid: Optional[str] = d['author_flair_template_id']
                self.text: str = d['author_flair_text'] or ''
                self.text_color: str = d['author_flair_text_color'] or ''
                self.type: str = d['author_flair_type']

        def __init__(self, d: Mapping[str, Any]):
            self.name: str = d['author']
            self.id36: str = d['author_fullname'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.has_premium: bool = d['author_premium']
            self.flair = self.AuthorFlair(d)

    class Submission:
        def __init__(self, d: Mapping[str, Any]):
            self.id36: str = d['link_id'].split('_', 1)[-1]
            self.id = int(self.id36, 36)

    class Subreddit:
        def __init__(self, d: Mapping[str, Any]):
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.name: str = d['subreddit']
            #: One of `public`, `private`, `restricted`, `archived`,
            #: `employees_only`, `gold_only`, `gold_restricted`, `user`.
            self.type: str = d['subreddit_type']

    class Moderator:
        def __init__(self, d: Mapping[str, Any]):
            self.spam: bool = d['spam']

            self.approved: bool = d['approved']
            self.approved_by: Optional[str] = d['approved_by']
            self.approved_ut: Optional[int] = d['approved_at_utc']
            self.approved_at: Optional[datetime] = None
            if self.approved_ut is not None:
                self.approved_at = datetime.fromtimestamp(self.approved_ut, timezone.utc)

            self.removed: bool = d['removed']

    THING_ID = 't1'

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.body: str = d['body']
        self.body_html: str = d['body_html']
        #: Works even if score is hidden (`hide_score` JSON field is `True`).
        self.score: int = d['score']
        self.score_hidden: bool = d['score_hidden']

        self.rel_permalink: str = d['permalink']
        self.permalink: str = AUTHORIZATION_BASE_URL + d['permalink']

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
        self.is_top_level: bool = _parent_id.startswith('t3_')
        self.parent_comment_id36: Optional[str] = None
        self.parent_comment_id: Optional[int] = None
        if _parent_id.startswith('t1_'):
            self.parent_comment_id36 = _parent_id.split('_', 1)[-1]
            self.parent_comment_id = int(self.parent_comment_id36, 36)

        self.user = self.User(d)

        self.submission = self.Submission(d)
        self.subreddit = self.Subreddit(d)

        s: str = d['author']
        self.author_name = s
        self.u_author_name = s
        self.author = None
        if not s.startswith('['):
            self.u_author_name = f'u/{s}'
            self.author = self.Author(d)

        self.mod = None
        # `spam`, `ignore_reports`, `approved`, `removed`, and `rte_mode`
        # are all fields that aren't available when the current user is
        # not a moderator of the subreddit (or there’s no user context).
        if 'spam' in d:
            self.mod = self.Moderator(d)


class NewCommentBase(CommentBase):
    # For comments originating from `/comments` or `/r/{subreddit}/comments`.

    class Submission(CommentBase.Submission):
        def __init__(self, d: Mapping[str, Any]):
            super().__init__(d)
            self.comment_count: int = d['num_comments']
            self.nsfw: bool = d['over_18']
            self.title: str = d['link_title']
            self.author_name: str = d['link_author']
            self.rel_permalink: str = d['link_permalink']
            self.permalink: str = AUTHORIZATION_BASE_URL + d['link_permalink']

    class Subreddit(CommentBase.Subreddit):
        def __init__(self, d: Mapping[str, Any]):
            super().__init__(d)
            self.quarantined: bool = d['quarantine']
