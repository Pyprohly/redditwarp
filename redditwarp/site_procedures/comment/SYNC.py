
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_SYNC import Comment as CommentModel

from ...models.load.comment_SYNC import load_comment
from ...util.base_conversion import to_base36
from .fetch_SYNC import Fetch
from .get_SYNC import Get
from .bulk_fetch_SYNC import BulkFetch

class Comment:
    def __init__(self, client: Client):
        self._client = client
        self.fetch = Fetch(self, client)
        self.get = Get(client)
        self.bulk_fetch = BulkFetch(client)

    def reply(self, comment_id: int, text: str) -> CommentModel:
        data = {
            'thing_id': 't1_' + to_base36(comment_id),
            'text': text,
            'return_rtjson': '1',
        }
        result = self._client.request('POST', '/api/comment', data=data)
        return load_comment(result, self._client)

    def edit_body(self, comment_id: int, text: str) -> CommentModel:
        data = {
            'thing_id': 't1_' + to_base36(comment_id),
            'text': text,
            'return_rtjson': '1',
        }
        result = self._client.request('POST', '/api/editusertext', data=data)
        return load_comment(result, self._client)

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
