
from __future__ import annotations
from typing import Mapping, Any, Optional

from datetime import datetime, timezone

from .artifact import Artifact

class BaseSubreddit(Artifact):
    class Me:
        class MeFlair:
            def __init__(self, d: Mapping[str, Any]):
                self.enabled: bool = d['user_sr_flair_enabled']
                self.has_had_flair: bool = d['user_flair_text'] is not None
                self.bg_color: str = d['user_flair_background_color'] or ''
                user_flair_css_class_temp: Optional[str] = d['user_flair_css_class']
                self.has_had_css_class_when_no_flair_template: bool = user_flair_css_class_temp is not None
                self.css_class: str = user_flair_css_class_temp or ''
                self.position: str = d['user_flair_position']
                self.template_uuid: Optional[str] = d['user_flair_template_id']
                self.text: str = d['user_flair_text'] or ''
                self.fg_light_or_dark: str = d['user_flair_text_color'] or ''
                self.type: str = d['user_flair_type']

        def __init__(self, d: Mapping[str, Any]):
            self.favorited: bool = d['user_has_favorited']
            self.is_banned: bool = d['user_is_banned']
            self.is_contributor: bool = d['user_is_contributor']
            self.is_moderator: bool = d['user_is_moderator']
            self.is_muted: bool = d['user_is_muted']
            self.is_subscribed: bool = d['user_is_subscriber']
            self.sr_theme_enabled: bool = d['user_sr_theme_enabled']
            self.flair: BaseSubreddit.Me.MeFlair = self.MeFlair(d)

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
        self.id: int = int(self.id36, 36)
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)

        self.name: str = d['display_name']
        self.type: str = d['subreddit_type']

        self.subscriber_count: int = d['subscribers']
        self.viewing_count: int = d['active_user_count']

        self.title: str = d['title']
        self.public_description: str = d['public_description']
        self.public_description_html: str = d['public_description_html']
        self.sidebar_description: str = d['description']
        self.sidebar_description_html: str = d['description_html']
        self.submitting_form_note: str = d['submit_text']
        self.submitting_form_note_html: str = d['submit_text_html']
        self.submit_text_label: str = d['submit_text_label']
        self.submit_link_label: str = d['submit_link_label']

        submission_type: str = d['submission_type']
        self.allows_text_submissions: bool = submission_type in ('any', 'self')
        self.allows_link_submissions: bool = submission_type in ('any', 'link')
        self.allows_gallery_submissions: bool = d['allow_galleries']
        self.allows_poll_submissions: bool = d['allow_polls']

        self.suggested_comment_sort: Optional[str] = d['suggested_comment_sort']

        self.nsfw: bool = d['over18']
        self.quarantined: bool = d['quarantine']

        self.icon_img: str = d['icon_img']

        self.me: Optional[BaseSubreddit.Me] = None
        if d['user_is_moderator'] is not None:
            self.me = self.Me(d)

        self.flair: BaseSubreddit.SubredditFlair = self.SubredditFlair(d)
