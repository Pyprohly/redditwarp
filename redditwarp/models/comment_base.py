
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence

from datetime import datetime, timezone

from ..auth.const import AUTHORIZATION_BASE_URL
from .artifact import Artifact
from .report import ModReport, UserReport
from .load.report import load_mod_report, load_user_report

class BaseComment(Artifact):
    class Me:
        def __init__(self, d: Mapping[str, Any]):
            self.saved: bool = d['saved']
            self.reply_notifications: bool = d['send_replies']
            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]

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
            self.flair: BaseComment.Author.AuthorFlair = self.AuthorFlair(d)

    class Submission:
        def __init__(self, d: Mapping[str, Any]):
            self.id36: str = d['link_id'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)

    class Subreddit:
        def __init__(self, d: Mapping[str, Any]):
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)
            self.name: str = d['subreddit']
            self.type: str = d['subreddit_type']

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

            self.approved: Optional[BaseComment.Moderator.Approved] = None
            if d['approved_by']:
                self.approved = self.Approved(d)

            self.removed: Optional[BaseComment.Moderator.Removed] = None
            if d['banned_by']:
                self.removed = self.Removed(d)

            self.reports: BaseComment.Moderator.Reports = self.Reports(d)

            self.removal_reason_by: Optional[str] = d['mod_reason_by']
            self.removal_reason_title: Optional[str] = d['mod_reason_title']
            self.removal_note: Optional[str] = d['mod_note']

    class _Edited:
        def __init__(self, d: Mapping[str, Any]):
            self.ut: int = d['edited']
            self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)

        self.body: str = d['body']
        self.body_html: str = d.get('body_html', '')
        #: Works even if score is hidden (`hide_score` JSON field is `True`).
        self.score: int = d['score']
        self.score_hidden: bool = d['score_hidden']

        self.rel_permalink: str = d['permalink']
        self.permalink: str = AUTHORIZATION_BASE_URL + self.rel_permalink

        self.edited: Optional[BaseComment._Edited] = None
        if d['edited']:
            self.edited = self._Edited(d)

        self.is_submitter: bool = d['is_submitter']
        self.stickied: bool = d['stickied']
        self.archived: bool = d['archived']
        self.locked: bool = d['locked']
        self.collapsed: bool = d['collapsed']
        self.distinguished: str = d['distinguished'] or ''

        parent_id: str = d['parent_id']
        self.is_top_level: bool = parent_id.startswith('t3_')
        self.parent_comment_id36: Optional[str] = None
        self.parent_comment_id: Optional[int] = None
        if parent_id.startswith('t1_'):
            self.parent_comment_id36 = parent_id.partition('_')[2]
            self.parent_comment_id = int(self.parent_comment_id36, 36)

        self.me: BaseComment.Me = self.Me(d)

        self.submission: BaseComment.Submission = self.Submission(d)
        self.subreddit: BaseComment.Subreddit = self.Subreddit(d)

        s: str = d['author']
        self.author_name: str = s
        self.author: Optional[BaseComment.Author] = None
        if not s.startswith('['):
            self.author = self.Author(d)

        self.mod: Optional[BaseComment.Moderator] = None
        if 'spam' in d:
            self.mod = self.Moderator(d)


class BaseExtraSubmissionFieldsComment(BaseComment):
    # For:
    # * `GET /comments`
    # * `GET /r/{subreddit}/comments`
    # * `GET /user/{username}/overview` (and variants)

    class Submission(BaseComment.Submission):
        def __init__(self, d: Mapping[str, Any]):
            super().__init__(d)
            self.comment_count: int = d['num_comments']
            self.nsfw: bool = d['over_18']
            self.title: str = d['link_title']
            self.author_name: str = d['link_author']
            self.rel_permalink: str = d['link_permalink']
            self.permalink: str = AUTHORIZATION_BASE_URL + self.rel_permalink

    class Subreddit(BaseComment.Subreddit):
        def __init__(self, d: Mapping[str, Any]):
            super().__init__(d)
            self.quarantined: bool = d['quarantine']

class BaseEditPostTextEndpointComment(BaseComment):
    # For: `POST /api/editusertext`
    pass
