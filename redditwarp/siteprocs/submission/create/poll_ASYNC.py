
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
        options: Sequence[str],
        duration: int,
        *,
        body: Optional[str] = None,
        reply_notifications: Optional[bool] = True,
        spoiler: Optional[bool] = False,
        nsfw: Optional[bool] = False,
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
            yield ('options', list(options))
            yield ('duration', duration)
            if body is not None: yield ('text', body)
            if reply_notifications is not None: yield ('sendreplies', reply_notifications)
            if spoiler is not None: yield ('spoiler', spoiler)
            if nsfw is not None: yield ('nsfw', nsfw)
            if collection_uuid is not None: yield ('collection_id', collection_uuid)
            if flair_uuid is not None: yield ('flair_id', flair_uuid)
            if flair_text is not None: yield ('flair_text', flair_text)
            if event_start is not None: yield ('event_start', event_start)
            if event_end is not None: yield ('event_end', event_end)
            if event_tz is not None: yield ('event_tz', event_tz)

        return await self._client.request('POST', '/api/submit_poll_post', json=dict(g()))
