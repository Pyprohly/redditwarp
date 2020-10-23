
from __future__ import annotations
from typing import Mapping, Any, Optional

from .original_reddit_thing_object import OriginalRedditThingObject

class SubredditBase(OriginalRedditThingObject):
    class User:
        def __init__(self, outer: SubredditBase, d: Mapping[str, Any]):
            self.has_favorited: bool = d['user_has_favorited']
            self.is_banned: bool = d['user_is_banned']
            self.is_contributor: bool = d['user_is_contributor']
            self.is_moderator: bool = d['user_is_moderator']
            self.is_muted: bool = d['user_is_muted']
            self.is_subscriber: bool = d['user_is_subscriber']
            self.sr_flair_enabled: bool = d['user_sr_flair_enabled']
            self.sr_theme_enabled: bool = d['user_sr_theme_enabled']

    THING_ID = 't5'

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.name: str = d['display_name']
        #: One of `public`, `private`, `restricted`, `archived`,
        #: `employees_only`, `gold_only`, or `gold_restricted`.
        self.type: str = d['subreddit_type']

        self.subscriber_count: int = d['subscribers']
        self.active_user_count: int = d['active_user_count']

        self.title: str = d['title']
        self.sidebar_description: str = d['description']
        self.sidebar_description_html: str = d['description_html']
        self.summary_description: str = d['public_description']
        self.summary_description_html: str = d['public_description_html']
        self.submitting_form_note: str = d['submit_text']
        self.submitting_form_note_html: str = d['submit_text_html']
        self.submit_text_label: str = d['submit_text_label']
        self.submit_link_label: str = d['submit_link_label']

        _submission_type: str = d['submission_type']
        self.allows_text_submissions = _submission_type in ('any', 'self')
        self.allows_link_submissions = _submission_type in ('any', 'link')

        #: One of `confidence` (best), `old`, `top`, `qa`, `controversial`, or `new`.
        self.suggested_comment_sort: Optional[str] = d['suggested_comment_sort']

        self.nsfw: bool = d['over18']
        self.quarantined: bool = d['quarantine']

        self.icon_img: str = d['icon_img']

        self.user = None
        if d['user_is_moderator'] is not None:
            self.user = self.User(self, d)
