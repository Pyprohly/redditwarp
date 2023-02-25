
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable, Union, Mapping
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_ASYNC import Comment
    from ...types import JSON_ro

import json

from ...model_loaders.comment_ASYNC import load_comment
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.async_call_chunk import AsyncCallChunk
from .fetch_ASYNC import Fetch
from .get_ASYNC import Get

class CommentProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.fetch: Fetch = Fetch(self, client)
        self.get: Get = Get(client)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingAsyncIterator[Comment]:
        async def mass_fetch(ids: Sequence[int]) -> Sequence[Comment]:
            id36s = map(to_base36, ids)
            full_id36s = map('t1_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = await self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_comment(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingAsyncIterator(AsyncCallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))

    async def reply(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> Comment:
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't1_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/comment', files=dict(g()))
        return load_comment(result, self._client)

    async def edit_body(self, idn: int, body: Union[str, Mapping[str, JSON_ro]]) -> Comment:
        def g() -> Iterable[tuple[str, str]]:
            yield ('thing_id', 't1_' + to_base36(idn))
            yield ('return_rtjson', '1')
            if isinstance(body, str):
                yield ('text', body)
            else:
                yield ('richtext_json', json.dumps(body))

        result = await self._client.request('POST', '/api/editusertext', files=dict(g()))
        return load_comment(result, self._client)

    async def delete(self, idn: int) -> None:
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/del', data=data)

    async def lock(self, idn: int) -> None:
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/lock', data=data)

    async def unlock(self, idn: int) -> None:
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/unlock', data=data)

    async def vote(self, idn: int, direction: int) -> None:
        data = {
            'id': 't1_' + to_base36(idn),
            'dir': str(direction),
        }
        await self._client.request('POST', '/api/vote', data=data)

    async def save(self, idn: int, category: Optional[str] = None) -> None:
        data = {
            'id': 't1_' + to_base36(idn),
        }
        if category is not None:
            data['category'] = category
        await self._client.request('POST', '/api/save', data=data)

    async def unsave(self, idn: int) -> None:
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/unsave', data=data)

    async def distinguish(self, idn: int) -> Comment:
        data = {
            'id': 't1_' + to_base36(idn),
            'how': 'yes',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def distinguish_and_sticky(self, idn: int) -> Comment:
        data = {
            'id': 't1_' + to_base36(idn),
            'how': 'yes',
            'sticky': '1',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def undistinguish(self, idn: int) -> Comment:
        data = {
            'id': 't1_' + to_base36(idn),
            'how': 'no',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def enable_reply_notifications(self, idn: int) -> None:
        data = {
            'id': 't1_' + to_base36(idn),
            'state': '1'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def disable_reply_notifications(self, idn: int) -> None:
        data = {
            'id': 't1_' + to_base36(idn),
            'state': '0'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def approve(self, idn: int) -> None:
        data = {'id': 't1_' + to_base36(idn)}
        await self._client.request('POST', '/api/approve', data=data)

    async def remove(self, idn: int) -> None:
        data = {
            'id': 't1_' + to_base36(idn),
            'spam': '0',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def remove_spam(self, idn: int) -> None:
        data = {
            'id': 't1_' + to_base36(idn),
            'spam': '1',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def ignore_reports(self, idn: int) -> None:
        await self._client.request('POST', '/api/ignore_reports', data={'id': 't1_' + to_base36(idn)})

    async def unignore_reports(self, idn: int) -> None:
        await self._client.request('POST', '/api/unignore_reports', data={'id': 't1_' + to_base36(idn)})

    async def snooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't1_' + to_base36(idn), 'reason': reason}
        await self._client.request('POST', '/api/snooze_reports', data=data)

    async def unsnooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't1_' + to_base36(idn), 'reason': reason}
        await self._client.request('POST', '/api/unsnooze_reports', data=data)

    async def apply_removal_reason(self,
            idn: int,
            reason_id: Optional[str] = None,
            note: Optional[str] = None) -> None:
        target = 't1_' + to_base36(idn)
        json_data = {'item_ids': [target], 'reason_id': reason_id, 'mod_note': note}
        await self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    async def send_removal_comment(self,
            idn: int,
            title: str,
            message: str,
            *,
            exposed: bool = False,
            locked: bool = False) -> Comment:
        target = 't1_' + to_base36(idn)
        json_data = {
            'type': 'public' + ('' if exposed else '_as_subreddit'),
            'item_id': [target],
            'title': title,
            'message': message,
            'lock_comment': '01'[locked],
        }
        root = await self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
        return load_comment(root, self._client)

    async def send_removal_message(self,
            idn: int,
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        target = 't1_' + to_base36(idn)
        json_data = {
            'type': 'private' + ('_exposed' if exposed else ''),
            'item_id': [target],
            'title': title,
            'message': message,
        }
        await self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
