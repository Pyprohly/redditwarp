
from __future__ import annotations
from typing import Mapping, Any

from datetime import datetime, timezone

class BaseLiveThread:
    def __init__(self, d: Mapping[str, Any]):
        self.d: Mapping[str, Any] = d
        self.idt: str = d['id']
        self.title: str = d['title']
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.description: str = d['description']
        self.description_html: str = d['description_html']
        self.resources: str = d['resources']
        self.resources_html: str = d['resources_html']
        self.websocket_url: str = d['websocket_url']
        self.is_closed: bool = d['state'] == 'complete'
        self.nsfw: bool = d['nsfw']
        self.viewer_count: int = d['viewer_count']

class BaseLiveUpdate:
    def __init__(self, d: Mapping[str, Any]):
        self.d: Mapping[str, Any] = d
        self.uuid: str = d['id']
        self.author_name: str = d['author']
        self.body: str = d['body']
        self.body_html: str = d['body_html']
        self.created_ut: int = int(d['created_utc'])
        self.created_at: datetime = datetime.fromtimestamp(self.created_ut, timezone.utc)
        self.stricken: bool = d['stricken']
