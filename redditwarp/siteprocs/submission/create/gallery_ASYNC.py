
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client
    from ....dtos.submission import GalleryItem
    from ....types import JSON_ro

class Gallery:
    def __init__(self, client: Client) -> None:
        self._client: Client = client

    async def __call__(self,
        sr: str,
        title: str,
        items: Sequence[GalleryItem],
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        oc: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> None:
        gallery_items: list[dict[str, str]] = [
            {
                'media_id': m.media_id,
                'caption': m.caption,
                'outbound_url': m.outbound_link,
            }
            for m in items
        ]

        def g() -> Iterable[tuple[str, JSON_ro]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('items', gallery_items)
            yield ('sendreplies', reply_notifications)
            if spoiler: yield ('spoiler', True)
            if nsfw: yield ('nsfw', True)
            if oc: yield ('original_content', True)
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        return await self._client.request('POST', '/api/submit_gallery_post', json=dict(g()))
