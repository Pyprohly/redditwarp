
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence

from datetime import datetime, timezone

from ..auth.const import AUTHORIZATION_BASE_URL
from .artifact import Artifact
from .reports import ModReport, UserReport
from .load.reports import load_mod_report, load_user_report

class BaseSubmission(Artifact):
    class _Me:
        def __init__(self, d: Mapping[str, Any]):
            # User context fields
            self.saved: bool = d['saved']  # False if no user context
            self.hidden: bool = d['hidden']  # False if no user context
            self.reply_notifications: bool = d['send_replies']  # False if no user context
            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]  # None if no user context
            self.is_following_event: bool = d.get('is_followed', False)  # False if no user context

    class _Author:
        class _AuthorFlair:
            def __init__(self, d: Mapping[str, Any]):
                self.template_uuid: Optional[str] = d['author_flair_template_id']
                author_flair_text: Optional[str] = d['author_flair_text']
                self.text: str = author_flair_text or ''
                self.has_had_flair: bool = author_flair_text is not None
                self.fg_light_or_dark: str = d['author_flair_text_color'] or ''
                self.bg_color: str = d['author_flair_background_color'] or ''
                self.uses_richtext: bool = d['author_flair_type'] == 'richtext'
                author_flair_css_class: Optional[str] = d['author_flair_css_class']
                self.has_had_css_class_when_no_flair_template: bool = author_flair_css_class is not None
                self.css_class: str = author_flair_css_class or ''

        def __init__(self, d: Mapping[str, Any]):
            self.name: str = d['author']
            self.id36: str = d['author_fullname'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)
            self.has_premium: bool = d['author_premium']
            self.flair: BaseSubmission._Author._AuthorFlair = self._AuthorFlair(d)

    class _Subreddit:
        def __init__(self, d: Mapping[str, Any]):
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)
            self.name: str = d['subreddit']
            #: One of `public`, `private`, `restricted`, `archived`,
            #: `employees_only`, `gold_only`, or `gold_restricted`.
            self.type: str = d['subreddit_type']
            self.quarantined: bool = d['quarantine']
            self.subscriber_count: int = d['subreddit_subscribers']

    class _Moderator:
        class _Approved:
            def __init__(self, d: Mapping[str, Any]):
                self.by: str = d['approved_by']
                self.ut: int = d['approved_at_utc']
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)

        class _Removed:
            def __init__(self, d: Mapping[str, Any]):
                self.by: str = d['banned_by']
                self.ut: int = d['banned_at_utc']
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)

        class _Reports:
            def __init__(self, d: Mapping[str, Any]):
                self.ignoring: bool = d['ignore_reports']
                self.num_reports: int = d['num_reports']
                self.mod_reports: Sequence[ModReport] = [load_mod_report(m) for m in d['mod_reports']]
                self.user_reports: Sequence[UserReport] = [load_user_report(m) for m in d['user_reports']]

        def __init__(self, d: Mapping[str, Any]):
            self.spam: bool = d['spam']

            self.approved: Optional[BaseSubmission._Moderator._Approved] = None
            if d['approved_by']:
                self.approved = self._Approved(d)

            self.removed: Optional[BaseSubmission._Moderator._Removed] = None
            if d['banned_by']:
                self.removed = self._Removed(d)

            self.reports: BaseSubmission._Moderator._Reports = self._Reports(d)

            self.removal_reason_by: Optional[str] = d['mod_reason_by']
            self.removal_reason_title: Optional[str] = d['mod_reason_title']
            self.removal_note: Optional[str] = d['mod_note']

    class _Event:
        def __init__(self, d: Mapping[str, Any]):
            self.start_ut: int = int(d['event_start'])
            self.start_at: datetime = datetime.fromtimestamp(self.start_ut, timezone.utc)
            self.end_ut: int = int(d['event_end'])
            self.end_at: datetime = datetime.fromtimestamp(self.end_ut, timezone.utc)
            self.is_live: bool = d['event_is_live']

    class _Flair:
        def __init__(self, d: Mapping[str, Any]):
            self.has_flair: bool = d['link_flair_text'] is not None
            self.bg_color: str = d['link_flair_background_color']
            link_flair_css_class_temp: Optional[str] = d['link_flair_css_class']
            self.css_class: str = link_flair_css_class_temp or ''
            self.template_uuid: Optional[str] = d.get('link_flair_template_id', None)
            self.text: str = d['link_flair_text'] or ''
            self.fg_light_or_dark: str = d['link_flair_text_color']
            self.type: str = d['link_flair_type']

    class _Reports:
        def __init__(self, d: Mapping[str, Any]):
            self.ignoring: bool = d['ignore_reports']
            self.num_reports: int = d['num_reports']
            self.mod_reports: Sequence[ModReport] = [load_mod_report(m) for m in d['mod_reports']]
            self.user_reports: Sequence[UserReport] = [load_user_report(m) for m in d['user_reports']]

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)

        self.title: str = d['title']
        #: Works even if score is hidden (`hide_score` JSON field is `True`).
        self.score: int = d['score']
        self.score_hidden: bool = d['hide_score']
        self.comment_count: int = d['num_comments']

        self.rel_permalink: str = d['permalink']
        self.permalink: str = AUTHORIZATION_BASE_URL + d['permalink']

        a: Any = d['edited']
        self.edited: bool = bool(a)
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
        self.oc: bool = d['is_original_content']
        self.robot_indexable: bool = d['is_robot_indexable']
        self.pinned: bool = d['pinned']
        self.distinguished: str = d['distinguished'] or ''

        self.event: Optional[BaseSubmission._Event] = None
        if 'event_start' in d:
            self.event = self._Event(d)

        self.me: BaseSubmission._Me = self._Me(d)

        self.subreddit: BaseSubmission._Subreddit = self._Subreddit(d)

        s: str = d['author']
        self.author_name: str = s
        self.author: Optional[BaseSubmission._Author] = None
        if not s.startswith('['):
            self.author = self._Author(d)

        self.mod: Optional[BaseSubmission._Moderator] = None
        # `spam`, `ignore_reports`, `approved`, `removed`, and `rte_mode`
        # are all fields that aren't available when the current user is
        # not a moderator of the subreddit (or there’s no user context).
        if 'spam' in d:
            self.mod = self._Moderator(d)

        self.flair: BaseSubmission._Flair = self._Flair(d)

        self.reports: Optional[BaseSubmission._Reports] = None
        if d['num_reports'] is not None:
            self.reports = self._Reports(d)


class BaseLinkPost(BaseSubmission):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.link: str = d['url_overridden_by_dest']

class BaseTextPost(BaseSubmission):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.body: str = d['selftext']
        self.body_html: str = d['selftext_html']

class BaseImagePost(BaseSubmission):
    pass

class BaseVideoPost(BaseSubmission):
    pass

class BaseGalleryPost(BaseSubmission):
    pass

class BasePollPost(BaseSubmission):
    pass

class BaseCrosspostPost(BaseSubmission):
    pass
