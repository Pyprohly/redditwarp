
from __future__ import annotations
from typing import Mapping, Any, Sequence, Optional

from datetime import datetime, timezone
from functools import cached_property

from ..core.const import AUTHORIZATION_BASE_URL

class CustomFeed:
    def __init__(self, d: Mapping[str, Any]) -> None:
        self.d: Mapping[str, Any] = d
        ("")
        self.owner: str = d['owner']
        ("""
            The curator of the custom feed.
            """)
        full_id36: str = d['owner_id']
        _, _, id36 = full_id36.partition('_')
        self.owner_id36: str = id36
        ("")
        self.owner_id: int = int(id36, 36)
        ("")
        self.name: str = d['name']
        ("")
        self.title: str = d['display_name']
        ("")
        self.description: str = d['description_md']
        ("")
        self.description_html: str = d['description_html']
        ("")
        self.subscriber_count: int = d['num_subscribers']
        ("")
        self.icon_url: str = d['icon_url']
        ("")
        self.subreddit_names: Sequence[str] = [o['name'] for o in d['subreddits']]
        ("")
        self.created_ut: int = int(d['created_utc'])
        ("")
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        ("")
        self.public: bool = d['visibility'] == 'public'
        ("")
        self.nsfw: bool = d['over_18']
        ("")
        self.rel_permalink: str = d['path']
        ("")
        self.permalink: str = AUTHORIZATION_BASE_URL + d['path']
        ("")
        self.copied_from: Optional[tuple[str, str]] = None
        ("""
            A tuple of (user, feed) if the custom feed is a copy.
            """)
        copied_from_path = d['copied_from']
        if copied_from_path:
            user, feed = copied_from_path.strip('/').split('/')[1::2]
            self.copied_from = (user, feed)

    class Me:
        def __init__(self, outer: CustomFeed) -> None:
            d = outer.d
            self.can_edit: bool = d['can_edit']
            ("")
            self.favorited: bool = d['is_favorited']
            ("""
                Whether the current user has favourited the custom feed. False if no user context.
                """)
            self.subscribed: bool = d['is_subscriber']
            ("""
                Whether the current user is following the custom feed. False if no user context.
                """)

    me: cached_property[Me] = cached_property(Me)
