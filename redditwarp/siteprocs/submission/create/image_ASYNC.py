
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, TypeVar, Protocol, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client

_YIntOrStr = TypeVar('_YIntOrStr', int, str)
_YIntOrStr_co = TypeVar('_YIntOrStr_co', int, str, covariant=True)

class Image:
    class GenericOverload(Protocol[_YIntOrStr_co]):
        async def __call__(self,
            sr: str,
            title: str,
            link: str,
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
        ) -> _YIntOrStr_co: ...

    def __init__(self, client: Client) -> None:
        self._client: Client = client

    async def __call__(self,
        sr: str,
        title: str,
        link: str,
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
            yield ('kind', 'image')
            yield ('sr', sr)
            yield ('title', title)
            yield ('url', link)
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

        await self._client.request('POST', '/api/submit', data=dict(g()))
