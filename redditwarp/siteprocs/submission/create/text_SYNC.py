
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union, Mapping, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....types import JSON_ro

import json

class Text:
    def __init__(self, client: Client) -> None:
        self._client: Client = client

    def __call__(self,
        sr: str,
        title: str,
        body: Optional[Union[str, Mapping[str, JSON_ro]]],
        *,
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
        def g() -> Iterable[tuple[str, str]]:
            yield ('kind', 'self')
            yield ('sr', sr)
            yield ('title', title)
            if body is not None:
                if isinstance(body, str):
                    yield ('text', body)
                else:
                    yield ('richtext_json', json.dumps(body))
            if reply_notifications is not None: yield ('sendreplies', '01'[reply_notifications])
            if spoiler is not None: yield ('spoiler', '01'[spoiler])
            if nsfw is not None: yield ('nsfw', '01'[nsfw])
            if oc is not None: yield ('original_content', '01'[oc])
            if collection_uuid is not None: yield ('collection_id', collection_uuid)
            if flair_uuid is not None: yield ('flair_id', flair_uuid)
            if flair_text is not None: yield ('flair_text', flair_text)
            if event_start is not None: yield ('event_start', event_start)
            if event_end is not None: yield ('event_end', event_end)
            if event_tz is not None: yield ('event_tz', event_tz)

        self._client.request('POST', '/api/submit', files=dict(g()))
