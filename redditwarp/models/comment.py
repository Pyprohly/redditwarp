
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence

from datetime import datetime, timezone

from ..core.const import AUTHORIZATION_BASE_URL
from .artifact import Artifact
from .report import ModReport, UserReport
from ..model_loaders.report import load_mod_report, load_user_report

class Comment(Artifact):
    @property
    def submission(self) -> Comment.Submission:
        return self.__submission

    @property
    def subreddit(self) -> Comment.Subreddit:
        return self.__subreddit

    class Me:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.saved: bool = d['saved']
            self.reply_notifications: bool = d['send_replies']
            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]

    class Author:
        class AuthorFlair:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.template_uuid: str = d['author_flair_template_id'] or ''
                author_flair_text: Optional[str] = d['author_flair_text']
                self.text: str = author_flair_text or ''
                self.has_had_flair: bool = author_flair_text is not None
                self.fg_light_or_dark: str = d['author_flair_text_color'] or ''
                self.bg_color: str = d['author_flair_background_color'] or ''
                self.uses_richtext: bool = d['author_flair_type'] == 'richtext'
                author_flair_css_class: Optional[str] = d['author_flair_css_class']
                self.has_had_css_class_when_no_flair_template: bool = author_flair_css_class is not None
                self.css_class: str = author_flair_css_class or ''

        def __init__(self, d: Mapping[str, Any]) -> None:
            self.name: str = d['author']
            self.id36: str = d['author_fullname'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)
            self.has_premium: bool = d['author_premium']
            self.flair: Comment.Author.AuthorFlair = self.AuthorFlair(d)

    class Submission:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.id36: str = d['link_id'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)

    class Subreddit:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            self.id: int = int(self.id36, 36)
            self.name: str = d['subreddit']
            self.openness: str = d['subreddit_type']

    class Moderator:
        class Approved:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.by: str = d['approved_by']
                self.ut: int = d['approved_at_utc']
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)

        class Removed:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.by: str = d['banned_by']
                self.ut: int = d['banned_at_utc']
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)

        class Reports:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.ignoring: bool = d['ignore_reports']
                self.num_reports: int = d['num_reports']
                self.mod_reports: Sequence[ModReport] = [load_mod_report(m) for m in d['mod_reports']]
                self.user_reports: Sequence[UserReport] = [load_user_report(m) for m in d['user_reports']]

        def __init__(self, d: Mapping[str, Any]) -> None:
            self.spam: bool = d['spam']

            self.approved: Optional[Comment.Moderator.Approved] = None
            if d['approved_by']:
                self.approved = self.Approved(d)

            self.removed: Optional[Comment.Moderator.Removed] = None
            if d['banned_by']:
                self.removed = self.Removed(d)

            self.reports: Comment.Moderator.Reports = self.Reports(d)

            self.has_removal_reason: bool = bool(d['mod_reason_by'])
            self.removal_reason_by: str = d['mod_reason_by'] or ''
            self.removal_reason_title: str = d['mod_reason_title'] or ''
            self.removal_note: str = d['mod_note'] or ''

    class Edited:
        def __init__(self, outer: Comment) -> None:
            self.ut: int = outer.edited_ut
            self.at: datetime = outer.edited_at

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)

        self.body: str = d['body']
        self.body_html: str = d.get('body_html', '')
        self.score: int = d['score']
        self.score_hidden: bool = d['score_hidden']

        self.rel_permalink: str = d['permalink']
        self.permalink: str = AUTHORIZATION_BASE_URL + self.rel_permalink

        edited: Any = d['edited']
        self.is_edited: bool = bool(edited)
        self.edited_ut: int = int(edited) if edited else 0
        self.edited_at: datetime = datetime.min
        if self.is_edited:
            self.edited_at = datetime.fromtimestamp(self.edited_ut, timezone.utc)

        self.edited: Optional[Comment.Edited] = None
        if edited:
            self.edited = self.Edited(self)

        self.is_submitter: bool = d['is_submitter']
        self.stickied: bool = d['stickied']
        self.archived: bool = d['archived']
        self.locked: bool = d['locked']
        self.collapsed: bool = d['collapsed']
        self.distinguished: str = d['distinguished'] or ''

        parent_id: str = d['parent_id']
        self.is_top_level: bool = parent_id.startswith('t3_')
        self.has_parent_comment: bool = not self.is_top_level
        self.parent_comment_id36: str = ''
        self.parent_comment_id: int = 0
        if self.has_parent_comment:
            self.parent_comment_id36 = parent_id.partition('_')[2]
            self.parent_comment_id = int(self.parent_comment_id36, 36)

        self.me: Comment.Me = self.Me(d)

        self.__submission: Comment.Submission = self.Submission(d)
        self.__subreddit: Comment.Subreddit = self.Subreddit(d)

        s: str = d['author']
        self.author_name: str = s
        self.author: Optional[Comment.Author] = None
        if not s.startswith('['):
            self.author = self.Author(d)

        self.mod: Optional[Comment.Moderator] = None
        if 'spam' in d:
            self.mod = self.Moderator(d)


class LooseComment(Comment):
    # For:
    # * `GET /comments`
    # * `GET /r/{subreddit}/comments`
    # * `GET /user/{username}/overview` (and variants)

    @property
    def submission(self) -> LooseComment.Submission:
        return self.__submission

    @property
    def subreddit(self) -> LooseComment.Subreddit:
        return self.__subreddit

    class Submission(Comment.Submission):
        def __init__(self, d: Mapping[str, Any]) -> None:
            super().__init__(d)
            self.title: str = d['link_title']
            self.author_name: str = d['link_author']
            self.rel_permalink: str = d['link_permalink']
            self.permalink: str = AUTHORIZATION_BASE_URL + self.rel_permalink
            self.nsfw: bool = d['over_18']

    class Subreddit(Comment.Subreddit):
        def __init__(self, d: Mapping[str, Any]) -> None:
            super().__init__(d)
            self.quarantined: bool = d['quarantine']

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.__submission: LooseComment.Submission = self.Submission(d)
        self.__subreddit: LooseComment.Subreddit = self.Subreddit(d)
