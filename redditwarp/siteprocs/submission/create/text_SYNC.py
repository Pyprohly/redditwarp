
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, TypeVar, Protocol, cast, Any, Union, Mapping, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....types import JSON_ro

import json

_YIntOrStr = TypeVar('_YIntOrStr', int, str)
_YIntOrStr_co = TypeVar('_YIntOrStr_co', int, str, covariant=True)

class Text:
    class GenericOverload(Protocol[_YIntOrStr_co]):
        def __call__(self,
            sr: str,
            title: str,
            body: Union[str, Mapping[str, JSON_ro]],
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

    def __call__(self,
        sr: str,
        title: str,
        body: Union[str, Mapping[str, JSON_ro]],
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
        self.__helper(
            sr=sr,
            title=title,
            body=body,
            reply_notifications=reply_notifications,
            spoiler=spoiler,
            nsfw=nsfw,
            oc=oc,
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

    def __helper(self,
        sr: str,
        title: str,
        body: Union[str, Mapping[str, JSON_ro]],
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
    ) -> Any:
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'self')
            yield ('sr', sr)
            yield ('title', title)
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))
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

        return self._client.request('POST', '/api/submit', files=dict(g()))

    def y_int(self,
        sr: str,
        title: str,
        body: Union[str, Mapping[str, JSON_ro]],
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
    ) -> int:
        root = self.__helper(
            sr=sr,
            title=title,
            body=body,
            reply_notifications=reply_notifications,
            spoiler=spoiler,
            nsfw=nsfw,
            oc=oc,
            collection_uuid=collection_uuid,
            flair_uuid=flair_uuid,
            flair_text=flair_text,
            event_start=event_start,
            event_end=event_end,
            event_tz=event_tz,
        )
        return int(root['json']['data']['id'], 36)

    def y_str(self,
        sr: str,
        title: str,
        body: Union[str, Mapping[str, JSON_ro]],
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
    ) -> str:
        root = self.__helper(
            sr=sr,
            title=title,
            body=body,
            reply_notifications=reply_notifications,
            spoiler=spoiler,
            nsfw=nsfw,
            oc=oc,
            collection_uuid=collection_uuid,
            flair_uuid=flair_uuid,
            flair_text=flair_text,
            event_start=event_start,
            event_end=event_end,
            event_tz=event_tz,
        )
        return root['json']['data']['id']
