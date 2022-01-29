
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_ASYNC import (
        Comment,
        EditPostTextEndpointComment,
    )

from ...models.load.comment_ASYNC import load_comment, load_edit_post_text_endpoint_comment
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_async_iterator import CallChunkChainingAsyncIterator
from ...iterators.call_chunk_ASYNC import CallChunk
from .fetch_ASYNC import Fetch
from .get_ASYNC import Get

class CommentProcedures:
    def __init__(self, client: Client):
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

        return CallChunkChainingAsyncIterator(CallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))

    async def reply(self, comment_id: int, text: str) -> Comment:
        data = {
            'thing_id': 't1_' + to_base36(comment_id),
            'text': text,
            'return_rtjson': '1',
        }
        result = await self._client.request('POST', '/api/comment', data=data)
        return load_comment(result, self._client)

    async def edit_body(self, comment_id: int, text: str) -> EditPostTextEndpointComment:
        data = {
            'thing_id': 't1_' + to_base36(comment_id),
            'text': text,
            'return_rtjson': '1',
        }
        result = await self._client.request('POST', '/api/editusertext', data=data)
        return load_edit_post_text_endpoint_comment(result, self._client)

    async def delete(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        await self._client.request('POST', '/api/del', data=data)

    async def lock(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        await self._client.request('POST', '/api/lock', data=data)

    async def unlock(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        await self._client.request('POST', '/api/unlock', data=data)

    async def vote(self, comment_id: int, direction: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'dir': str(direction),
        }
        await self._client.request('POST', '/api/vote', data=data)

    async def save(self, comment_id: int, category: Optional[str] = None) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
        }
        if category is not None:
            data['category'] = category
        await self._client.request('POST', '/api/save', data=data)

    async def unsave(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        await self._client.request('POST', '/api/unsave', data=data)

    async def distinguish(self, comment_id: int) -> Comment:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'how': 'yes',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def distinguish_and_sticky(self, comment_id: int) -> Comment:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'how': 'yes',
            'sticky': '1',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def undistinguish(self, comment_id: int) -> Comment:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'how': 'no',
        }
        root = await self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    async def enable_reply_notifications(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'state': '1'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def disable_reply_notifications(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'state': '0'
        }
        await self._client.request('POST', '/api/sendreplies', data=data)

    async def approve(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        await self._client.request('POST', '/api/approve', data=data)

    async def remove(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'spam': '0',
        }
        await self._client.request('POST', '/api/remove', data=data)

    async def remove_spam(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
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
            comment_id: int,
            reason_id: Optional[str],
            note: Optional[str] = None) -> None:
        target = 't1_' + to_base36(comment_id)
        json_data = {'item_ids': [target], 'reason_id': reason_id, 'mod_note': note}
        await self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    async def send_removal_comment(self,
            comment_id: int,
            title: str,
            message: str) -> Comment:
        target = 't1_' + to_base36(comment_id)
        json_data = {
            'type': 'public',
            'item_id': [target],
            'title': title,
            'message': message,
        }
        root = await self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
        return load_comment(root, self._client)

    async def send_removal_message(self,
            comment_id: int,
            title: str,
            message: str,
            *,
            exposed: bool = False) -> None:
        target = 't1_' + to_base36(comment_id)
        json_data = {
            'type': 'private' + ('_exposed' if exposed else ''),
            'item_id': [target],
            'title': title,
            'message': message,
        }
        await self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
