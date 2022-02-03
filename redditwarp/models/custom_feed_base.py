
from __future__ import annotations
from typing import Mapping, Any, Sequence

from datetime import datetime, timezone
from functools import cached_property

from ..auth.const import AUTHORIZATION_BASE_URL

class BaseCustomFeed:
    def __init__(self, d: Mapping[str, Any]):
        self.d: Mapping[str, Any] = d
        self.title: str = d['display_name']
        self.name: str = d['name']
        self.description: str = d['description_md']
        self.description_html: str = d['description_html']
        self.subscriber_count: int = d['num_subscribers']
        self.icon_url: str = d['icon_url']
        self.subreddit_names: Sequence[str] = [o['name'] for o in d['subreddits']]
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.private: bool = d['visibility'] == 'private'
        self.nsfw: bool = d['over_18']
        self.rel_permalink: str = d['path']
        self.permalink: str = AUTHORIZATION_BASE_URL + d['path']
        self.copied_from: str = d['copied_from']
        self.owner: str = d['owner']

        full_id36: str = d['owner_id']
        _, _, id36 = full_id36.partition('_')
        self.owner_id36: str = id36
        self.owner_id: int = int(id36, 36)

    class _me:
        def __init__(self, outer: BaseCustomFeed):
            d = outer.d
            self.can_edit: bool = d['can_edit']
            self.favorited: bool = d['is_favorited']
            self.is_subscribed: bool = d['is_subscriber']

    me: cached_property[_me] = cached_property(_me)
