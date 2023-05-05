
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, TypeVar, Protocol, cast, Any, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client
    from ....types import JSON_ro

_YIntOrStr = TypeVar('_YIntOrStr', int, str)
_YIntOrStr_co = TypeVar('_YIntOrStr_co', int, str, covariant=True)

class Poll:
    class GenericOverload(Protocol[_YIntOrStr_co]):
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
        ) -> _YIntOrStr_co: ...

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
        await self.__helper(
            sr=sr,
            title=title,
            body=body,
            options=options,
            duration=duration,
            reply_notifications=reply_notifications,
            spoiler=spoiler,
            nsfw=nsfw,
            collection_uuid=collection_uuid,
            flair_uuid=flair_uuid,
            flair_text=flair_text,
            event_start=event_start,
            event_end=event_end,
            event_tz=event_tz,
        )

    def __getitem__(self, key: type[_YIntOrStr]) -> GenericOverload[_YIntOrStr]:
        d = {
            int: self.y_int,
            str: self.y_str,
        }
        try:
            v = d[key]
        except KeyError as e:
            raise TypeError from e
        # https://github.com/python/mypy/issues/4177
        return cast("__class__.GenericOverload[_YIntOrStr]", cast(object, v))  # type: ignore[name-defined]

    async def __helper(self,
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
    ) -> Any:
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

    async def y_int(self,
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
    ) -> int:
        root = await self.__helper(
            sr=sr,
            title=title,
            body=body,
            options=options,
            duration=duration,
            reply_notifications=reply_notifications,
            spoiler=spoiler,
            nsfw=nsfw,
            collection_uuid=collection_uuid,
            flair_uuid=flair_uuid,
            flair_text=flair_text,
            event_start=event_start,
            event_end=event_end,
            event_tz=event_tz,
        )
        return int(root['json']['data']['id'][3:], 36)

    async def y_str(self,
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
    ) -> str:
        root = await self.__helper(
            sr=sr,
            title=title,
            body=body,
            options=options,
            duration=duration,
            reply_notifications=reply_notifications,
            spoiler=spoiler,
            nsfw=nsfw,
            collection_uuid=collection_uuid,
            flair_uuid=flair_uuid,
            flair_text=flair_text,
            event_start=event_start,
            event_end=event_end,
            event_tz=event_tz,
        )
        return root['json']['data']['id'][3:]
