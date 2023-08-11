
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ....util.base_conversion import to_base36

class Cross:
    def __init__(self, client: Client) -> None:
        self._client: Client = client

    async def __call__(self,
        sr: str,
        title: str,
        target: Union[int, str],
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
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'crosspost')
            yield ('sr', sr)
            yield ('title', title)
            id36 = x if isinstance((x := target), str) else to_base36(x)
            yield ('crosspost_fullname', 't3_' + id36)
            yield ('sendreplies', '01'[reply_notifications])
            if spoiler: yield ('spoiler', '1')
            if nsfw: yield ('nsfw', '1')
            if oc: yield ('original_content', '1')
            if collection_uuid: yield ('collection_id', collection_uuid)
            if flair_uuid: yield ('flair_id', flair_uuid)
            if flair_text: yield ('flair_text', flair_text)
            if event_start: yield ('event_start', event_start)
            if event_end: yield ('event_end', event_end)
            if event_tz: yield ('event_tz', event_tz)

        return await self._client.request('POST', '/api/submit', data=dict(g()))
