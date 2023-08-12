
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....dtos.submission import GalleryItem
    from ....types import JSON_ro

class Gallery:
    def __init__(self, client: Client) -> None:
        self._client: Client = client

    def __call__(self,
        sr: str,
        title: str,
        items: Sequence[GalleryItem],
        *,
        body: Optional[str] = None,
        reply_notifications: Optional[bool] = True,
        spoiler: Optional[bool] = False,
        nsfw: Optional[bool] = False,
        oc: Optional[bool] = False,
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
            if body is not None: yield ('text', body)
            if reply_notifications is not None: yield ('sendreplies', reply_notifications)
            if spoiler is not None: yield ('spoiler', spoiler)
            if nsfw is not None: yield ('nsfw', nsfw)
            if oc is not None: yield ('original_content', oc)
            if collection_uuid is not None: yield ('collection_id', collection_uuid)
            if flair_uuid is not None: yield ('flair_id', flair_uuid)
            if flair_text is not None: yield ('flair_text', flair_text)
            if event_start is not None: yield ('event_start', event_start)
            if event_end is not None: yield ('event_end', event_end)
            if event_tz is not None: yield ('event_tz', event_tz)

        return self._client.request('POST', '/api/submit_gallery_post', json=dict(g()))
