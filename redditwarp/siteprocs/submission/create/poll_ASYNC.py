
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client
    from ....types import JSON_ro

class Poll:
    def __init__(self, client: Client) -> None:
        self._client: Client = client

    async def __call__(self,
        sr: str,
        title: str,
        body: str,
        options: Sequence[str],
        duration: int,
        *,
        reply_notifications: bool = True,
        spoiler: bool = False,
        nsfw: bool = False,
        collection_uuid: Optional[str] = None,
        flair_uuid: Optional[str] = None,
        flair_text: Optional[str] = None,
        event_start: Optional[str] = None,
        event_end: Optional[str] = None,
        event_tz: Optional[str] = None,
    ) -> None:
        def g() -> Iterable[tuple[str, JSON_ro]]:
            yield ('sr', sr)
            yield ('title', title)
            yield ('text', body)
            yield ('options', options)
            yield ('duration', duration)
            yield ('sendreplies', reply_notifications)
            if spoiler: yield ('spoiler', True)
            if nsfw: yield ('nsfw', True)
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        return await self._client.request('POST', '/api/submit_poll_post', json=dict(g()))
