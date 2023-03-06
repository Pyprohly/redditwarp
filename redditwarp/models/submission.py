
from __future__ import annotations
from typing import Mapping, Any, Optional, Sequence, TypeVar, Callable, final

from datetime import datetime, timezone

from ..core.const import AUTHORIZATION_BASE_URL
from .datamemento import DatamementoBase
from .report import ModReport, UserReport
from ..model_loaders.report import load_mod_report, load_user_report
from dataclasses import dataclass

class Submission(DatamementoBase):
    class Me:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.saved: bool = d['saved']
            ("""
                Whether the current user has saved the post.

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
            self.hidden: bool = d['hidden']
            ("""
                Whether the current user has hidden the post.

                Value false if there is not user context.
                """)
            self.is_following_event: bool = d.get('is_followed', False)
            ("""
                True if the submisison has event details and is being followed by the current user.

                Value false if there is no user context.
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
                    The author's flair text.

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
            self.id: int = int(self.id36, 36)
            ("")
            self.has_premium: bool = d['author_premium']
            ("")
            self.flair: Submission.Author.AuthorFlair = self.AuthorFlair(d)
            ("")

    class Subreddit:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.id36: str = d['subreddit_id'].split('_', 1)[-1]
            ("")
            self.id: int = int(self.id36, 36)
            ("")
            self.name: str = d['subreddit']
            ("")
            self.openness: str = d['subreddit_type']
            ("""
                Either: `public`, `private`, `restricted`, `archived`,
                `employees_only`, `gold_only`, `gold_restricted`, or `user`.
                """)
            self.quarantined: bool = d['quarantine']
            ("")
            self.subscriber_count: int = d['subreddit_subscribers']
            ("")

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

            self.approved: Optional[Submission.Moderation.Approved] = None
            ("")
            if d['approved_by']:
                self.approved = self.Approved(d)

            self.removed: Optional[Submission.Moderation.Removed] = None
            ("")
            if d['banned_by']:
                self.removed = self.Removed(d)

            self.reports: Submission.Moderation.Reports = self.Reports(d)
            ("")

            self.removal_reason: Optional[Submission.Moderation.RemovalReason] = None
            ("")
            if d['mod_reason_by']:
                self.removal_reason = self.RemovalReason(d)

    class Event:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.start_ut: int = int(d['event_start'])
            ("")
            self.start_at: datetime = datetime.fromtimestamp(self.start_ut, timezone.utc)
            ("")
            self.end_ut: int = int(d['event_end'])
            ("")
            self.end_at: datetime = datetime.fromtimestamp(self.end_ut, timezone.utc)
            ("")
            self.is_live: bool = d['event_is_live']
            ("")

    class Flair:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.template_uuid: Optional[str] = d.get('link_flair_template_id')
            ("""
                The post flair template UUID.

                Value is null if no flair template is being used.
                """)
            self.text_mode: str = d['link_flair_type']
            ("""
                Either `text` or `richtext`.
                """)
            self.text: str = d['link_flair_text'] or ''
            ("""
                The flair text.
                """)
            self.css_class: str = d['link_flair_css_class'] or ''
            ("""
                Post flair CSS class.

                When a flair template is being used, the value of this field will be
                that of the CSS class designated by the template. If the flair template
                does not specify a CSS class then the value will be an empty string.
                """)
            # Post flairs can't be `transparent` but just in case.
            self.bg_color: str = '' if (x := d['link_flair_background_color']) == 'transparent' else x
            ("""A background color hex string. E.g., `#46d160`.

                If a flair template is not being used then the value is an empty string.

                A post flair template background color cannot be unset unlike user flair templates.
                """)
            self.fg_color_scheme: str = d['link_flair_text_color']
            ("""
                Either `dark` or `light`, or empty string.

                Value is empty string if a flair template is not being used.
                """)

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

    class Edited:
        def __init__(self, outer: Submission) -> None:
            self.ut: int = outer.edited_ut
            ("")
            self.at: datetime = outer.edited_at
            ("")

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.id36: str = d['id']
        ("""
            The ID of the submission as a base 36 number.
            """)
        self.id: int = int(self.id36, 36)
        ("")
        self.created_ut: int = int(d['created_utc'])
        ("""
            Unix timestamp of when the submission was made.
            """)
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("""
            When the submission was made.
            """)

        self.title: str = d['title']
        ("")
        self.score: int = d['score']
        ("""
            The number of upvotes (minus downvotes).
            """)
        self.score_hidden: bool = d['hide_score']
        ("""
            Whether the score should be hidden.
            """)
        self.comment_count: int = d['num_comments']
        ("""
            The number of comments.

            This should be treated as an estimation and may not match
            the number of actual visible comments. It could be higher or lower.
            """)

        self.permalink_path: str = d['permalink']
        ("""
            The URL of the submission, without the domain.
            """)
        self.permalink: str = AUTHORIZATION_BASE_URL + self.permalink_path
        ("""
            The URL of the submission.
            """)

        edited: Any = d['edited']
        self.is_edited: bool = bool(edited)
        ("""
            True if the submission was edited.
            """)
        self.edited_ut: int = int(edited) if edited else 0
        ("""
            Unix timestamp of when the submission was edited.

            Value is `0` if :attr:`is_edited` is false.
            """)
        self.edited_at: datetime = datetime.min
        ("""
            When the submission was edited.

            Value is `datetime.min` if :attr:`is_edited` is false.
            """)
        if self.is_edited:
            self.edited_at = datetime.fromtimestamp(self.edited_ut, timezone.utc)

        self.edited: Optional[Submission.Edited] = None
        ("""
            Value non-`None` if the comment was edited.
            """)
        if edited:
            self.edited = self.Edited(self)

        self.upvote_ratio: float = d['upvote_ratio']
        ("")
        self.removal_category: Optional[str] = d['removed_by_category']
        ("""
            `None` if not removed.

            If removed, possible values:

                `author`, `anti_evil_ops`, `community_ops`, `legal_operations`, `copyright_takedown`,
                `reddit`, `user`, `deleted`, `moderator`, `automod_filtered`.
            """)
        self.suggested_sort: str = d['suggested_sort'] or ''
        ("""
            Either: `confidence` (best), `new`, `old`, `top`, `qa`, `controversial`, or `live`.

            Value empty string if not set.
            """)
        self.stickied: bool = d['stickied']
        ("")
        self.archived: bool = d['archived']
        ("""
            Whether the post is archived.

            Archived posts cannot be commented on,
            but the author can still edit the OP.
            """)
        self.locked: bool = d['locked']
        ("")
        self.in_contest_mode: bool = d['contest_mode']
        ("""
            Whether the post is in contest mode.

            In contest mode, the comments are shown in a random order.
            """)
        self.nsfw: bool = d['over_18']
        ("")
        self.spoiler: bool = d['spoiler']
        ("")
        self.oc: bool = d['is_original_content']
        ("""
            Whether the post is marked as 'original content'.
            """)
        self.num_crossposts: int = d['num_crossposts']
        ("""
            Crosspost count.
            """)
        self.is_crosspostable: bool = d['is_crosspostable']
        ("""
            Whether the post can be crossposted.

            Will be `false` if the post was removed or deleted.
            """)
        self.is_robot_indexable: bool = d['is_robot_indexable']
        ("""
            Whether search engines should index this submission.

            Will be `false` if the post was removed or deleted.
            """)
        self.is_poster_profile_pinned: bool = d['pinned']
        ("""
            Whether the post is pinned to the poster's profile.

            This attribute can only be true if the submission object was obtained through a user listing.
            """)
        self.distinguished: str = d['distinguished'] or ''
        ("""
            Either `moderator` or `admin`, or empty string.

            Value empty string if not distinguished.
            """)

        self.event: Optional[Submission.Event] = None
        ("""
            Attributes related to event metadata of the submission.
            """)
        if 'event_start' in d:
            self.event = self.Event(d)

        self.me: Submission.Me = self.Me(d)
        ("""
            Attributes relating to the current user.

            If there is no user context, these values contain nonsense.
            """)

        self.subreddit: Submission.Subreddit = self.Subreddit(d)
        ("""
            Information related to the submission's subreddit.
            """)

        author: str = d['author']
        self.author_display_name: str = author
        ("""
            The author's username.

            Possibly `[removed]` if the submission was removed or
            `[deleted]` if the submission was deleted by the author.
            """)
        self.author: Optional[Submission.Author] = None
        ("""
            Information about the author.

            Value is `None` if the submission was removed or deleted.
            """)
        if not author.startswith('['):
            self.author = self.Author(d)

        self.mod: Optional[Submission.Moderation] = None
        ("""
            Attributes relating to moderation.

            Value is `None` if the current user is not a moderator of the subreddit.
            """)
        if 'spam' in d:
            self.mod = self.Moderation(d)

        self.flair: Submission.Flair = self.Flair(d)
        ("""
            Attributes related to the author's flair.
            """)

        self.reports: Optional[Submission.Reports] = None
        ("")
        if d['num_reports'] is not None:
            self.reports = self.Reports(d)


class LinkPost(Submission):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.link: str = d['url_overridden_by_dest']
        ("""
            The URL linked to by the link post.
            """)

class TextPost(Submission):
    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.body: str = d['selftext']
        ("""
            The body text of the submission. In markdown format.
            """)
        self.body_html: str = d['selftext_html']
        ("""
            The HTML of the submission.
            """)

class GalleryPost(Submission):
    @dataclass(repr=False, eq=False)
    class GalleryItem:
        id: int
        media_id: str
        caption: str
        outbound_link: str

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.gallery_link: str = d['url_overridden_by_dest']
        ("")

        gallery_data_items: Sequence[Any] = ()
        if gallery_data := d.get('gallery_data'):
            gallery_data_items = gallery_data['items']
        self.gallery: Sequence[GalleryPost.GalleryItem] = [
            self.GalleryItem(
                id=m['id'],
                media_id=m['media_id'],
                caption=m.get('caption', ''),
                outbound_link=m.get('outbound_url', ''),
            )
            for m in gallery_data_items
        ]
        ("")

class PollPost(Submission):
    pass

class CrosspostSubmission(Submission):
    @property
    def original(self) -> Optional[Submission]:
        """Original submission of this crosspost.

        Value `None` if the original submission is from a subreddit that is
        now banned and the submission is no longer accessible.
        """
        return self.__original

    def __init__(self, d: Mapping[str, Any]) -> None:
        super().__init__(d)
        self.original_id36: str = d['crosspost_parent'][3:]
        ("")
        self.original_id: int = int(self.original_id36, 36)
        ("")

        self.__original: Optional[Submission] = None
        # https://github.com/python/mypy/issues/4177
        if self.__class__.original == __class__.original:  # type: ignore[name-defined]
            from ..model_loaders.submission import load_submission  # Avoid cyclic import
            self.__original = self._load_original(d, load_submission)

    _TSubmission = TypeVar('_TSubmission', bound=Submission)

    @final
    def _load_original(self,
        d: Mapping[str, Any],
        load: Callable[[Mapping[str, Any]], _TSubmission],
    ) -> Optional[_TSubmission]:
        if crosspost_parent_list := d['crosspost_parent_list']:
            return load(crosspost_parent_list[0])
        return None
