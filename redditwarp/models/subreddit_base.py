
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .artifact import Artifact

class Subreddit(Artifact):
    class Me:
        class MeFlair:
            def __init__(self, d: Mapping[str, Any]):
                self.enabled: bool = d['user_sr_flair_enabled']

                # Ever had a flair before on the subreddit.
                self.has_had_flair: bool = d['user_flair_text'] is not None

                # empty string:
                #   * No flair template.
                # 'transparent':
                #   * Flair template being used but no background color set.
                # otherwise:
                #   * A color hex string, starting with '#'.
                self.bg_color: str = d['user_flair_background_color'] or ''

                _user_flair_css_class_temp: Optional[str] = d['user_flair_css_class']
                self.has_had_css_class_when_no_flair_template: bool = _user_flair_css_class_temp is not None

                # `None`:
                #   * Flair not configured.
                #   * A flair template is being used and the CSS class was never set before.
                # empty string:
                #   * Starts off as empty string if no flair template is being used.
                #   * CSS class was removed on a flair template.
                self.css_class: str = _user_flair_css_class_temp or ''

                # Values: `left` or `right`.
                self.position: str = d['user_flair_position']

                # `None`:
                #   * Flair not using a template.
                self.template_uuid: Optional[str] = d['user_flair_template_id']

                self.text: str = d['user_flair_text'] or ''
                self.text_color: str = d['user_flair_text_color'] or ''

                # Values: `text` or `richtext`.
                self.type: str = d['user_flair_type']

        def __init__(self, d: Mapping[str, Any]):
            self.favorited: bool = d['user_has_favorited']
            self.is_banned: bool = d['user_is_banned']
            self.is_contributor: bool = d['user_is_contributor']
            self.is_moderator: bool = d['user_is_moderator']
            self.is_muted: bool = d['user_is_muted']
            self.is_subscribed: bool = d['user_is_subscriber']
            self.sr_theme_enabled: bool = d['user_sr_theme_enabled']
            self.flair = self.MeFlair(d)

    class SubredditFlair:
        def __init__(self, d: Mapping[str, Any]):
            self.user_flairs_enabled: bool = d['user_flair_enabled_in_sr']
            self.link_flairs_enabled: bool = d['link_flair_enabled']
            self.users_can_assign_user_flair: bool = d['can_assign_user_flair']
            self.users_can_assign_link_flair: bool = d['can_assign_link_flair']
            self.user_flair_position: str = d['user_flair_position']
            self.link_flair_position: str = d['link_flair_position']

    def __init__(self, d: Mapping[str, Any]):
        super().__init__(d)
        self.id36: str = d['id']
        self.id = int(self.id36, 36)
        self.created_ut = int(d['created_utc'])
        self.created_at = datetime.fromtimestamp(self.created_ut, timezone.utc)

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

        self.me = None
        # Just checking if a user context is available.
        if d['user_is_moderator'] is not None:
            self.me = self.Me(d)

        self.flair = self.SubredditFlair(d)
