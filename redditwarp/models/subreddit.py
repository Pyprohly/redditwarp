
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .artifact import IArtifact

class Subreddit(IArtifact):
    class Me:
        class Flair:
            def __init__(self, d: Mapping[str, Any]) -> None:
                self.enabled: bool = False if (x := d['user_sr_flair_enabled']) is None else x
                ("""Whether the current user has their flair enabled in the subreddit.

                    Value is `False` if the subreddit object comes from a search item.""")

                flair_text: Optional[str] = d['user_flair_text']
                flair_css_class: Optional[str] = d['user_flair_css_class']

                self.template_uuid: Optional[str] = x if (x := d['user_flair_template_id']) else None
                ("""
                    The current user's flair template UUID in the subreddit.

                    Value is `None` if no flair template is being used.
                    """)
                self.text_mode: str = d['user_flair_type']
                ("""
                    Either `text` or `richtext`.
                    """)
                self.text: str = flair_text or ''
                ("""
                    The flair text.

                    Check if the value is an empty string to tell if a flair is being used.
                    """)
                self.css_class: str = flair_css_class or ''
                ("""
                    The current user's flair CSS class.

                    When a flair template is being used, the value of this field will be
                    that of the CSS class designated by the template. If the flair template
                    does not specify a CSS class then the value will be an empty string.
                    """)
                self.bg_color: str = '' if (x := d['user_flair_background_color']) == 'transparent' else x
                ("""
                    A background color hex string. E.g., `#46d160`.

                    If a flair template is not being used then the value will be an empty string.

                    If a flair template is being used and the background color is unset then
                    the value is an empty string.
                    """)
                self.fg_color_scheme: str = d['user_flair_text_color'] or ''
                ("""
                    Either `dark` or `light`, or empty string.

                    Value is empty string if a flair template is not being used.
                    """)

                self.has_had_flair_assigned_before_in_subreddit: bool = flair_text is not None
                ("""
                    Because of quirks in the API, we can tell if the user has ever had flair assigned before in the subreddit.
                    """)
                self.has_had_flair_css_class_assigned_before_in_subreddit_when_no_flair_template_assigned: bool = flair_css_class is not None
                ("""
                    Because of quirks in the API, we can tell if the user has ever had a flair CSS class
                    assigned before in the subreddit, but this only works if a flair template is not being used.
                    """)

        def __init__(self, d: Mapping[str, Any]) -> None:
            self.favorited: bool = d['user_has_favorited']
            self.is_banned: bool = d['user_is_banned']
            self.is_approved_user: bool = d['user_is_contributor']
            self.is_moderator: bool = d['user_is_moderator']
            ("""
                Whether the current user is a moderator of the subreddit.
                """)
            self.is_muted: bool = d['user_is_muted']
            self.is_subscribed: bool = d['user_is_subscriber']
            self.sr_theme_enabled: bool = d['user_sr_theme_enabled']
            ("""
                Whether the current user allows subreddit custom CSS.

                This is the "allow subreddits to show me custom themes" preference in old reddit.
                """)
            self.flair: Subreddit.Me.Flair = self.Flair(d)
            ("""
                Information about the current user's flair settings in the subreddit.
                """)

    class SubredditFlair:
        def __init__(self, d: Mapping[str, Any]) -> None:
            self.user_flairs_enabled: bool = d['user_flair_enabled_in_sr']
            ("""
                Whether user flairs are enabled in the subreddit.

                In old Reddit this is the flair option that says "enable user flair in this subreddit".

                Caution: Value is false if object was retrieved from a search. This isn't the case with
                the other variables.
                """)
            self.post_flairs_enabled: bool = d['link_flair_enabled']
            ("""Whether post flairs are enabled in the subreddit.

                In old Reddit, this field is tied to the 'link flair position' flair setting:
                the value is false when set to `none`.
                """)
            self.users_can_assign_user_flair: bool = d['can_assign_user_flair']
            ("""
                Whether or not users can assign a flair to themselves in this subreddit.

                If false, only a moderator can assign flairs to users.

                In old Reddit this is the flair option that says "allow users to assign their own flair".
                """)
            self.users_can_assign_post_flair: bool = d['can_assign_link_flair']
            ("""
                Whether or not users can assign a flair to their submission in this subreddit.

                If false, only a moderator can assign flairs to submissions.

                In old Reddit this is the flair option that says "allow submitters to assign their own link flair".
                """)
            self.user_flair_position: str = d['user_flair_position']
            ("""
                Either `left` or `right`, or empty string.

                Starts off as `right` in new subreddits.

                Can be set to an empty string via API calls
                (see :meth:`~.redditwarp.siteprocs.flair.SYNC.FlairProcedures.configure_subreddit_flair_settings`)
                but not through the UI.
                If an empty string then all user flairs are hidden, despite the :attr:`user_flairs_enabled` setting.
                """)
            self.post_flair_position: str = d['link_flair_position']
            ("""
                Either `left` or `right`, or empty string.

                Value is empty string if :attr:`post_flairs_enabled` is false (the 'none' option in the old Reddit UI).
                """)

    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.id36: str = d['id']
        ("""
            The ID of the subreddit as a base 36 number.
            """)
        self.id: int = int(self.id36, 36)
        ("""
            The subreddit ID.
            """)
        self.name: str = d['display_name']
        ("""
            The name of the subreddit.
            """)
        self.openness: str = d['subreddit_type']
        ("""
            Either: `public`, `private`, `restricted`, `archived`,
            `employees_only`, `gold_only`, `gold_restricted`, or `user`.
            """)
        self.created_ut: int = int(d['created_utc'])
        ("""
            Unix timestamp of when the subreddit was created.
            """)
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("""
            When the subreddit was created.
            """)

        self.title: str = d['title']
        ("""
            The title of the subreddit.

            Max. chars.: 100.
            """)
        self.public_description: str = d['public_description']
        self.public_description_html: str = d['public_description_html']
        self.sidebar_description: str = d['description']
        self.sidebar_description_html: str = d['description_html']
        self.submitting_form_note: str = d['submit_text']
        self.submitting_form_note_html: str = d['submit_text_html']
        self.submit_text_label: str = d['submit_text_label'] or ''
        ("""
            Custom label text for the "Submit a new text post" button.

            In old Reddit this is the "Custom label for submit text post button" subreddit option.
            """)
        self.submit_link_label: str = d['submit_link_label'] or ''
        ("""
            Custom label text for the "Custom label for submit link button" button.

            In old Reddit this is the "Custom label for submit text post button" subreddit option.
            """)

        self.subscriber_count: int = d['subscribers']
        self.viewing_count: int = -1 if (x := d['active_user_count']) is None else x
        ("""
            The number of online users who are subscribed to the subreddit.

            Value is `-1` if object was retrieved from a search.
            """)

        submission_type: str = d['submission_type']
        self.accepts_text_submissions: bool = submission_type in ('any', 'self')
        self.accepts_link_submissions: bool = submission_type in ('any', 'link')
        self.accepts_gallery_submissions: bool = d['allow_galleries']
        self.accepts_poll_submissions: bool = d['allow_polls']

        self.suggested_comment_sort: str = d['suggested_comment_sort'] or ''
        ("""
            Either: `confidence` (best), `new`, `old`, `top`, `qa`, `controversial`, or `live`.

            Value is empty string if not set.
            """)

        self.nsfw: bool = d['over18']
        self.quarantined: bool = d['quarantine']

        self.me: Optional[Subreddit.Me] = None
        ("""
            Attributes related to the current user.
            """)
        if d['user_is_moderator'] is not None:
            self.me = self.Me(d)

        self.flair: Subreddit.SubredditFlair = self.SubredditFlair(d)

        self.has_menu_widget: bool = d['has_menu_widget']
        ("""
            True if the subreddit has a menu widget active, otherwise false.

            Value is false if the object was retrieved from a search.
            """)


class InaccessibleSubreddit(IArtifact):
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        self.id36: str = d['id']
        self.id: int = int(self.id36, 36)
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)

        self.name: str = d['display_name']
        self.openness: str = d['subreddit_type']

        self.title: str = d['title']
