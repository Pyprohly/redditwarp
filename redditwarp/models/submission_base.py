
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .original_reddit_thing_object import OriginalRedditThingObject
from ..auth.const import AUTHORIZATION_BASE_URL

class SubmissionBase(OriginalRedditThingObject):
    class User:
        def __init__(self, outer: SubmissionBase, d: Mapping[str, Any]):
            # User context fields
            self.saved: bool = d['saved']  # False if no user context
            self.hidden: bool = d['hidden']  # False if no user context
            self.inbox_notifications: bool = d['send_replies']  # False if no user context
            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]  # None if no user context
            self.is_following_event: bool = d.get('is_followed', False)  # False if no user context

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

        def __init__(self, outer: SubmissionBase, d: Mapping[str, Any]):
            self.name: str = d['author']
            self.id36: str = d['author_fullname'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.has_premium: bool = d['author_premium']
            self.flair = self.AuthorFlair(d)

    class Subreddit:
        def __init__(self, outer: SubmissionBase, d: Mapping[str, Any]):
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id = int(self.id36, 36)
            self.name: str = d['subreddit']
            self.r_name = 'r/' + self.name
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

    class Event:
        def __init__(self, d: Mapping[str, Any]):
            self.start_ut = int(d['event_start'])
            self.start_at = datetime.fromtimestamp(self.start_ut, timezone.utc)
            self.end_ut = int(d['event_end'])
            self.end_at = datetime.fromtimestamp(self.end_ut, timezone.utc)
            self.is_live: bool = d['event_is_live']

    class Flair:
        def __init__(self, outer: SubmissionBase, d: Mapping[str, Any]):
            self.has_flair: bool = d['link_flair_text'] is not None
            self.bg_color: str = d['link_flair_background_color']
            _link_flair_css_class_temp: Optional[str] = d['link_flair_css_class']
            self.css_class: str = _link_flair_css_class_temp or ''
            self.template_uuid: Optional[str] = d.get('link_flair_template_id', None)
            self.text: str = d['link_flair_text'] or ''
            self.text_color: str = d['link_flair_text_color']
            self.type: str = d['link_flair_type']

    THING_ID = 't3'

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

        self.event = None
        if 'event_start' in d:
            self.event = self.Event(d)

        self.user = self.User(self, d)

        self.subreddit = self.Subreddit(self, d)

        s: str = d['author']
        self.author_name = s
        self.u_author_name = s
        self.author = None
        if not s.startswith('['):
            self.u_author_name = f'u/{s}'
            self.author = self.Author(self, d)

        self.mod = None
        # `spam`, `ignore_reports`, `approved`, `removed`, and `rte_mode`
        # are all fields that aren't available when the current user is
        # not a moderator of the subreddit (or there’s no user context).
        if 'spam' in d:
            self.mod = self.Moderator(self, d)

        self.flair = self.Flair(self, d)


class TextPostBase(SubmissionBase):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.body: str = d['selftext']
        self.body_html: str = d['selftext_html']

class LinkPostBase(SubmissionBase):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.link_url: str = d['url_overridden_by_dest']
