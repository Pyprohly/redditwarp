
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import (
        Comment as CommentModel,
        EditPostTextEndpointComment as EditPostTextEndpointCommentModel,
    )

from ...models.load.comment_SYNC import load_comment, load_edit_post_text_endpoint_comment
from ...util.base_conversion import to_base36
from ...iterators.chunking import chunked
from ...iterators.call_chunk_chaining_iterator import CallChunkChainingIterator
from ...iterators.call_chunk_SYNC import CallChunk
from .fetch_SYNC import Fetch
from .get_SYNC import Get

class Comment:
    def __init__(self, client: Client):
        self._client = client
        self.fetch: Fetch = Fetch(self, client)
        self.get: Get = Get(client)

    def bulk_fetch(self, ids: Iterable[int]) -> CallChunkChainingIterator[int, CommentModel]:
        def mass_fetch(ids: Sequence[int]) -> Sequence[CommentModel]:
            id36s = map(to_base36, ids)
            full_id36s = map('t1_'.__add__, id36s)
            ids_str = ','.join(full_id36s)
            root = self._client.request('GET', '/api/info', params={'id': ids_str})
            return [load_comment(i['data'], self._client) for i in root['data']['children']]

        return CallChunkChainingIterator(
                CallChunk(mass_fetch, idfs) for idfs in chunked(ids, 100))

    def reply(self, comment_id: int, text: str) -> CommentModel:
        data = {
            'thing_id': 't1_' + to_base36(comment_id),
            'text': text,
            'return_rtjson': '1',
        }
        result = self._client.request('POST', '/api/comment', data=data)
        return load_comment(result, self._client)

    def edit_body(self, comment_id: int, text: str) -> EditPostTextEndpointCommentModel:
        data = {
            'thing_id': 't1_' + to_base36(comment_id),
            'text': text,
            'return_rtjson': '1',
        }
        result = self._client.request('POST', '/api/editusertext', data=data)
        return load_edit_post_text_endpoint_comment(result, self._client)

    def delete(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        self._client.request('POST', '/api/del', data=data)

    def lock(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        self._client.request('POST', '/api/lock', data=data)

    def unlock(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        self._client.request('POST', '/api/unlock', data=data)

    def vote(self, comment_id: int, direction: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'dir': str(direction),
        }
        self._client.request('POST', '/api/vote', data=data)

    def save(self, comment_id: int, category: Optional[str] = None) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
        }
        if category is not None:
            data['category'] = category
        self._client.request('POST', '/api/save', data=data)

    def unsave(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        self._client.request('POST', '/api/unsave', data=data)

    def distinguish(self, comment_id: int) -> CommentModel:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'how': 'yes',
        }
        root = self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    def distinguish_and_sticky(self, comment_id: int) -> CommentModel:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'how': 'yes',
            'sticky': '1',
        }
        root = self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    def undistinguish(self, comment_id: int) -> CommentModel:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'how': 'no',
        }
        root = self._client.request('POST', '/api/distinguish', data=data)
        return load_comment(root['json']['data']['things'][0]['data'], self._client)

    def enable_reply_notifications(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'state': '1'
        }
        self._client.request('POST', '/api/sendreplies', data=data)

    def disable_reply_notifications(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'state': '0'
        }
        self._client.request('POST', '/api/sendreplies', data=data)

    def approve(self, comment_id: int) -> None:
        data = {'id': 't1_' + to_base36(comment_id)}
        self._client.request('POST', '/api/approve', data=data)

    def remove(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'spam': '0',
        }
        self._client.request('POST', '/api/remove', data=data)

    def remove_spam(self, comment_id: int) -> None:
        data = {
            'id': 't1_' + to_base36(comment_id),
            'spam': '1',
        }
        self._client.request('POST', '/api/remove', data=data)

    def ignore_reports(self, idn: int) -> None:
        self._client.request('POST', '/api/ignore_reports', data={'id': 't1_' + to_base36(idn)})

    def unignore_reports(self, idn: int) -> None:
        self._client.request('POST', '/api/unignore_reports', data={'id': 't1_' + to_base36(idn)})

    def snooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't1_' + to_base36(idn), 'reason': reason}
        self._client.request('POST', '/api/snooze_reports', data=data)

    def unsnooze_reports(self, idn: int, reason: str) -> None:
        data = {'id': 't1_' + to_base36(idn), 'reason': reason}
        self._client.request('POST', '/api/unsnooze_reports', data=data)

    def apply_removal_reason(self,
            comment_id: int,
            reason_id: Optional[str],
            note: Optional[str] = None) -> None:
        target = 't1_' + to_base36(comment_id)
        json_data = {'item_ids': [target], 'reason_id': reason_id, 'mod_note': note}
        self._client.request('POST', '/api/v1/modactions/removal_reasons', json=json_data)

    def send_removal_comment(self,
            comment_id: int,
            title: str,
            message: str) -> CommentModel:
        target = 't1_' + to_base36(comment_id)
        json_data = {
            'type': 'public',
            'item_id': [target],
            'title': title,
            'message': message,
        }
        root = self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
        return load_comment(root, self._client)

    def send_removal_message(self,
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
        self._client.request('POST', '/api/v1/modactions/removal_comment_message', json=json_data)
