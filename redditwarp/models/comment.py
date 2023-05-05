
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence

from datetime import datetime, timezone

from ..core.const import AUTHORIZATION_BASE_URL
from .datamemento import DatamementoBase
from .report import ModReport, UserReport
from ..model_loaders.report import load_mod_report, load_user_report

class Comment(DatamementoBase):
    @property
    def submission(self) -> Comment.Submission:
        """Information related to the comment's submission."""
        return self.__submission

    @property
    def subreddit(self) -> Comment.Subreddit:
        """Information related to the comment's subreddit."""
        return self.__subreddit

    class Me:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.saved: bool = d['saved']
            ("""
                Whether the current user has saved the comment.

                Value false if there is no user context.
                """)
            self.reply_notifications: bool = d['send_replies']
            ("""
                Whether an inbox message will be sent to you when the submission receives a new top-level comment.

                Value true if you are not the author of the submission.

                Value true if there is no user context.
                """)
            self.voted: int = {False: -1, None: 0, True: 1}[d['likes']]
            ("""
                Value `1` if upvoted, `0` if not voted on, `-1` if downvoted.
                """)

    class Author:
        class AuthorFlair:
            def __init__(self, d: Mapping[str, Any]) -> None:
                flair_text: Optional[str] = d['author_flair_text']
                flair_css_class: Optional[str] = d['author_flair_css_class']

                self.template_uuid: Optional[str] = x if (x := d['author_flair_template_id']) else None
                ("""
                    The author's flair template UUID.

                    Value is null if no flair template is being used.
                    """)
                self.text_mode: str = d['author_flair_type']
                ("""
                    Either `text` or `richtext`.
                    """)
                self.text: str = flair_text or ''
                ("""
                    Flair text.

                    Check if the value is an empty string to tell if a flair is being used.
                    """)
                self.css_class: str = flair_css_class or ''
                ("""
                    The author's flair CSS class.

                    When a flair template is being used, the value of this field will be
                    that of the CSS class designated by the template. If the flair template
                    does not specify a CSS class then the value will be an empty string.
                    """)
                self.bg_color: str = '' if (x := d['author_flair_background_color']) == 'transparent' else x
                ("""
                    A background color hex string. E.g., `#46d160`.

                    If a flair template is not being used then the value is an empty string.

                    If a flair template is being used and the background color is unset then
                    the value is an empty string.
                    """)
                self.fg_color_scheme: str = d['author_flair_text_color'] or ''
                ("""
                    Either `dark` or `light`, or empty string.

                    Value is empty string if a flair template is not being used.
                    """)

                self.has_had_flair_assigned_before_in_subreddit: bool = flair_text is not None
                ("""
                    Because of quirks in the API, we can tell if the user has ever had a flair assigned before in the subreddit.
                    """)
                self.has_had_flair_css_class_assigned_before_in_subreddit_when_no_flair_template_assigned: bool = flair_css_class is not None
                ("""
                    Because of quirks in the API, we can tell if the user has ever had a flair CSS class
                    assigned before in the subreddit. This only works if a flair template is not being used.
                    """)

        def __init__(self, d: Mapping[str, Any]) -> None:
            self.name: str = d['author']
            ("")
            self.id36: str = d['author_fullname'].split('_', 1)[-1]
            ("")
            self.idn: int = int(self.id36, 36)
            ("")
            self.id: int = self.idn
            ("")
            self.has_premium: bool = d['author_premium']
            ("")
            self.flair: Comment.Author.AuthorFlair = self.AuthorFlair(d)
            ("""
                Attributes related to the author's flair.
                """)

    class Submission:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.id36: str = d['link_id'].split('_', 1)[-1]
            ("")
            self.idn: int = int(self.id36, 36)
            ("")
            self.id: int = self.idn
            ("")
            self.archived: bool = d['archived']
            ("""
                Whether the post is archived.

                Archived posts cannot be commented on,
                but the author can still edit the OP.
                """)

    class Subreddit:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            ("")
            self.idn: int = int(self.id36, 36)
            ("")
            self.id: int = self.idn
            ("")
            self.name: str = d['subreddit']
            ("")
            self.openness: str = d['subreddit_type']
            ("""
                One of: `public`, `private`, `restricted`, `archived`,
                `employees_only`, `gold_only`, `gold_restricted`, or `user`.
                """)

    class Moderation:
        class Approved:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.by: str = d['approved_by']
                ("""
                    Name of the moderator who approved this comment.
                    """)
                self.ut: int = d['approved_at_utc']
                ("")
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)
                ("")

        class Removed:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.by: str = d['banned_by']
                ("""
                    Name of the moderator who removed this comment.
                    """)
                self.ut: int = d['banned_at_utc']
                ("")
                self.at: datetime = datetime.fromtimestamp(self.ut, timezone.utc)
                ("")

        class Reports:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.ignoring: bool = d['ignore_reports']
                ("")
                self.num_reports: int = d['num_reports']
                ("")
                self.mod_reports: Sequence[ModReport] = [load_mod_report(m) for m in d['mod_reports']]
                ("")
                self.user_reports: Sequence[UserReport] = [load_user_report(m) for m in d['user_reports']]
                ("")

        class RemovalReason:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.by: str = d['mod_reason_by'] or ''
                ("")
                self.title: str = d['mod_reason_title'] or ''
                ("")
                self.note: str = d['mod_note'] or ''
                ("")

        def __init__(self, d: Mapping[str, Any]) -> None:
            self.spam: bool = d['spam']
            ("")

            self.approved: Optional[Comment.Moderation.Approved] = None
            ("")
            if d['approved_by']:
                self.approved = self.Approved(d)

            self.removed: Optional[Comment.Moderation.Removed] = None
            ("")
            if d['banned_by']:
                self.removed = self.Removed(d)

            self.reports: Comment.Moderation.Reports = self.Reports(d)
            ("")

            self.removal_reason: Optional[Comment.Moderation.RemovalReason] = None
            ("")
            if d['mod_reason_by']:
                self.removal_reason = self.RemovalReason(d)

    class Edited:
        def __init__(self, outer: Comment) -> None:
            self.ut: int = outer.edited_ut
            ("")
            self.at: datetime = outer.edited_at
            ("")

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.id36: str = d['id']
        ("""
            ID of the comment as a base 36 number.
            """)
        self.idn: int = int(self.id36, 36)
        ("")
        self.id: int = self.idn
        ("")
        self.created_ut: int = int(d['created_utc'])
        ("""
            Unix timestamp of when the comment was made.
            """)
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("""
            When the comment was made.
            """)

        self.body: str = d['body']
        ("""
            Body text of the comment. In markdown format.
            """)
        self.body_html: str = d.get('body_html', '')
        ("""
            HTML of the comment.
            """)
        self.score: int = d['score']
        ("""
            Number of upvotes (minus downvotes).
            """)
        self.score_hidden: bool = d['score_hidden']
        ("""
            Whether the score should be hidden.
            """)

        self.permalink_path: str = d['permalink']
        ("""
            URL of the comment, without the domain.
            """)
        self.permalink: str = AUTHORIZATION_BASE_URL + self.permalink_path
        ("""
            URL of the comment.
            """)

        edited: Any = d['edited']
        self.is_edited: bool = bool(edited)
        ("""
            True if the comment was edited.
            """)
        self.edited_ut: int = int(edited) if edited else 0
        ("""
            Unix timestamp of when the comment was edited.

            Value is `0` if :attr:`is_edited` is false.
            """)
        self.edited_at: datetime = datetime.min
        ("""
            When the comment was edited.

            Value is `datetime.min` if :attr:`is_edited` is false.
            """)
        if self.is_edited:
            self.edited_at = datetime.fromtimestamp(self.edited_ut, timezone.utc)

        self.edited: Optional[Comment.Edited] = None
        ("""
            Value non-`None` if the comment was edited.
            """)
        if edited:
            self.edited = self.Edited(self)

        self.is_submitter: bool = d['is_submitter']
        ("""
            True if the author of this comment is the submission author ("OP").
            """)
        self.stickied: bool = d['stickied']
        ("")
        self.locked: bool = d['locked']
        ("")
        self.collapsed: bool = d['collapsed']
        ("""
            Whether the comment is collapsed by default, i.e., when it has been downvoted significantly.
            """)
        self.distinguished: str = d['distinguished'] or ''
        ("""
            Empty string if not distinguished, otherwise `'moderator'` or `'admin'`.
            """)

        parent_id: str = d['parent_id']
        self.is_top_level: bool = parent_id.startswith('t3_')
        ("""
            Whether the comment is a direct child of the submission.
            """)
        self.has_parent_comment: bool = not self.is_top_level
        ("""
            Same as `not self.is_top_level`.
            """)
        self.parent_comment_id36: str = ''
        ("""
            Parent comment ID36.

            Empty string if not applicable.
            """)
        self.parent_comment_idn: int = 0
        ("""
            Parent comment ID.

            Value is `0` if not applicable.
            """)
        if self.has_parent_comment:
            self.parent_comment_id36 = parent_id.partition('_')[2]
            self.parent_comment_idn = int(self.parent_comment_id36, 36)
        self.parent_comment_id: int = self.parent_comment_idn
        ("""
            Same as :attr:`parent_comment_idn`.
            """)

        self.me: Comment.Me = self.Me(d)
        ("""
            Attributes relating to the current user.

            If there is no user context, these values contain nonsense.
            """)

        self.__submission: Comment.Submission = self.Submission(d)
        self.__subreddit: Comment.Subreddit = self.Subreddit(d)

        s: str = d['author']
        self.author_display_name: str = s
        ("""
            The author's username.

            Possibly `[removed]` if the comment was removed or
            `[deleted]` if the comment was deleted by the author.
            """)
        self.author: Optional[Comment.Author] = None
        ("""
            Information about the author.

            Value is `None` if the comment was removed or deleted.
            """)
        if not s.startswith('['):
            self.author = self.Author(d)

        self.mod: Optional[Comment.Moderation] = None
        ("""
            Attributes relating to moderation.

            Value is `None` if the current user is not a moderator of the subreddit.
            """)
        if 'spam' in d:
            self.mod = self.Moderation(d)


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
            ("")
            self.author_display_name: str = d['link_author']
            ("")
            self.permalink_path: str = d['link_permalink']
            ("")
            self.permalink: str = AUTHORIZATION_BASE_URL + self.permalink_path
            ("")
            self.nsfw: bool = d['over_18']
            ("")

    class Subreddit(Comment.Subreddit):
        def __init__(self, d: Mapping[str, Any]) -> None:
            super().__init__(d)
            self.quarantined: bool = d['quarantine']
            ("")

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.__submission: LooseComment.Submission = self.Submission(d)
        self.__subreddit: LooseComment.Subreddit = self.Subreddit(d)
