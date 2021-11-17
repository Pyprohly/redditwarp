
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence, Generic, TypeVar

from datetime import datetime, timezone

from ..auth.const import AUTHORIZATION_BASE_URL
from .artifact import Artifact
from .report import ModReport, UserReport
from .load.report import load_mod_report, load_user_report

from dataclasses import dataclass

class BaseSubmission(Artifact):
    class Me:
        def __init__(self, d: Mapping[str, Any]):
            self.saved: bool = d['saved']
            self.hidden: bool = d['hidden']
            self.reply_notifications: bool = d['send_replies']
            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]
            self.is_following_event: bool = d.get('is_followed', False)

    class Author:
        class AuthorFlair:
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
            self.flair: BaseSubmission.Author.AuthorFlair = self.AuthorFlair(d)

    class Subreddit:
        def __init__(self, d: Mapping[str, Any]):
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)
            self.name: str = d['subreddit']
            self.type: str = d['subreddit_type']
            self.quarantined: bool = d['quarantine']
            self.subscriber_count: int = d['subreddit_subscribers']

    class Moderator:
        class Approved:
            def __init__(self, d: Mapping[str, Any]):
                self.by: str = d['approved_by']
                self.ut: int = d['approved_at_utc']
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)

        class Removed:
            def __init__(self, d: Mapping[str, Any]):
                self.by: str = d['banned_by']
                self.ut: int = d['banned_at_utc']
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)

        class Reports:
            def __init__(self, d: Mapping[str, Any]):
                self.ignoring: bool = d['ignore_reports']
                self.num_reports: int = d['num_reports']
                self.mod_reports: Sequence[ModReport] = [load_mod_report(m) for m in d['mod_reports']]
                self.user_reports: Sequence[UserReport] = [load_user_report(m) for m in d['user_reports']]

        def __init__(self, d: Mapping[str, Any]):
            self.spam: bool = d['spam']

            self.approved: Optional[BaseSubmission.Moderator.Approved] = None
            if d['approved_by']:
                self.approved = self.Approved(d)

            self.removed: Optional[BaseSubmission.Moderator.Removed] = None
            if d['banned_by']:
                self.removed = self.Removed(d)

            self.reports: BaseSubmission.Moderator.Reports = self.Reports(d)

            self.removal_reason_by: Optional[str] = d['mod_reason_by']
            self.removal_reason_title: Optional[str] = d['mod_reason_title']
            self.removal_note: Optional[str] = d['mod_note']

    class Event:
        def __init__(self, d: Mapping[str, Any]):
            self.start_ut: int = int(d['event_start'])
            self.start_at: datetime = datetime.fromtimestamp(self.start_ut, timezone.utc)
            self.end_ut: int = int(d['event_end'])
            self.end_at: datetime = datetime.fromtimestamp(self.end_ut, timezone.utc)
            self.is_live: bool = d['event_is_live']

    class Flair:
        def __init__(self, d: Mapping[str, Any]):
            self.has_flair: bool = d['link_flair_text'] is not None
            self.bg_color: str = d['link_flair_background_color']
            link_flair_css_class_temp: Optional[str] = d['link_flair_css_class']
            self.css_class: str = link_flair_css_class_temp or ''
            self.template_uuid: Optional[str] = d.get('link_flair_template_id', None)
            self.text: str = d['link_flair_text'] or ''
            self.fg_light_or_dark: str = d['link_flair_text_color']
            self.type: str = d['link_flair_type']

    class Reports:
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
        self.suggested_sort: Optional[str] = d['suggested_sort']
        self.stickied: bool = d['stickied']
        self.archived: bool = d['archived']
        self.locked: bool = d['locked']
        self.in_contest_mode: bool = d['contest_mode']
        self.nsfw: bool = d['over_18']
        self.spoiler: bool = d['spoiler']
        self.num_crossposts: int = d['num_crossposts']
        self.is_crosspostable: bool = d['is_crosspostable']
        self.is_original_content: bool = d['is_original_content']
        self.is_robot_indexable: bool = d['is_robot_indexable']
        self.pinned: bool = d['pinned']
        self.distinguished: str = d['distinguished'] or ''

        self.event: Optional[BaseSubmission.Event] = None
        if 'event_start' in d:
            self.event = self.Event(d)

        self.me: BaseSubmission.Me = self.Me(d)

        self.subreddit: BaseSubmission.Subreddit = self.Subreddit(d)

        author: str = d['author']
        self.author_name: str = author
        self.author: Optional[BaseSubmission.Author] = None
        if not author.startswith('['):
            self.author = self.Author(d)

        self.mod: Optional[BaseSubmission.Moderator] = None
        if 'spam' in d:
            self.mod = self.Moderator(d)

        self.flair: BaseSubmission.Flair = self.Flair(d)

        self.reports: Optional[BaseSubmission.Reports] = None
        if d['num_reports'] is not None:
            self.reports = self.Reports(d)


class BaseLinkPost(BaseSubmission):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.link: str = d['url_overridden_by_dest']

class BaseTextPost(BaseSubmission):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.body: str = d['selftext']
        self.body_html: str = d['selftext_html']

class BaseGalleryPost(BaseSubmission):
    @dataclass(repr=False, eq=False)
    class GalleryItem:
        id: int
        media_id: str
        caption: str
        outbound_link: str

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.gallery_link: str = d['url_overridden_by_dest']
        self.gallery: Sequence[BaseGalleryPost.GalleryItem] = [
            self.GalleryItem(
                id=m['id'],
                media_id=m['media_id'],
                caption=m.get('caption', ''),
                outbound_link=m.get('outbound_url', ''),
            )
            for m in d['gallery_data']['items']
        ]

class BasePollPost(BaseSubmission):
    pass


TOriginalSubmission = TypeVar('TOriginalSubmission', bound=BaseSubmission)

class GenericBaseCrosspostSubmission(BaseSubmission, Generic[TOriginalSubmission]):
    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.original_id36: str = d['crosspost_parent'][3:]
        self.original_id: int = int(self.original_id36, 36)
        self.original: TOriginalSubmission = self._load_submission(d['crosspost_parent_list'][0])

    def _load_submission(self, d: Mapping[str, Any]) -> TOriginalSubmission:
        raise NotImplementedError
