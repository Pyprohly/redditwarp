
from __future__ import annotations

import pytest

from redditwarp.models.subreddit import Subreddit


def _make_subreddit_data(**overrides) -> dict:
    """Build a minimal subreddit API response dict.

    All required fields are populated with sensible defaults.
    Pass keyword arguments to override or remove specific fields.
    """
    data = {
        'id': '2qh1i',
        'display_name': 'AskReddit',
        'subreddit_type': 'public',
        'created_utc': 1201233135.0,
        'title': 'Ask Reddit...',
        'public_description': 'A subreddit for asking questions.',
        'public_description_html': '<p>A subreddit for asking questions.</p>',
        'description': 'Rules and sidebar text.',
        'description_html': '<p>Rules and sidebar text.</p>',
        'submit_text': '',
        'submit_text_html': None,
        'submit_text_label': None,
        'submit_link_label': None,
        'subscribers': 48000000,
        'active_user_count': 15000,
        'submission_type': 'any',
        'allow_galleries': True,
        'allow_polls': True,
        'suggested_comment_sort': None,
        'over18': False,
        'quarantine': False,
        'user_is_moderator': None,
        'user_is_subscriber': None,
        'user_flair_enabled_in_sr': None,
        'user_sr_flair_enabled': None,
        'user_flair_text': None,
        'user_flair_css_class': None,
        'user_flair_background_color': None,
        'user_flair_text_color': None,
        'user_flair_template_id': None,
        'can_assign_user_flair': False,
        'can_assign_link_flair': False,
        'user_flair_position': 'right',
        'link_flair_enabled': True,
        'link_flair_position': 'left',
        'has_menu_widget': False,
    }
    data.update(overrides)
    return data


class TestSubredditConstruction:
    """Test Subreddit model construction from API response dicts."""

    def test_basic_construction(self):
        """Subreddit can be constructed from a complete API response."""
        data = _make_subreddit_data()
        subr = Subreddit(data)
        assert subr.name == 'AskReddit'
        assert subr.subscriber_count == 48000000
        assert subr.viewing_count == 15000

    def test_active_user_count_none(self):
        """viewing_count is -1 when active_user_count is None (e.g., search results)."""
        data = _make_subreddit_data(active_user_count=None)
        subr = Subreddit(data)
        assert subr.viewing_count == -1

    def test_active_user_count_missing(self):
        """viewing_count is -1 when active_user_count is absent from API response.

        Reddit removed this field from some API endpoints circa 2025.
        Previously this raised KeyError.
        """
        data = _make_subreddit_data()
        del data['active_user_count']
        subr = Subreddit(data)
        assert subr.viewing_count == -1

    def test_active_user_count_zero(self):
        """viewing_count is 0 when active_user_count is 0."""
        data = _make_subreddit_data(active_user_count=0)
        subr = Subreddit(data)
        assert subr.viewing_count == 0
