
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import ComposedMessage

from functools import cached_property

from ...util.base_conversion import to_base36
from ...models.load.message_SYNC import load_composed_message
from .pull_SYNC import Pull

class Message:
    def __init__(self, client: Client):
        self._client = client
        self.pull = Pull(client)

    def send(self, to: str, subject: str, body: str) -> None:
        req_data = {
            'to': to,
            'subject': subject,
            'text': body,
        }
        self._client.request('POST', '/api/compose', data=req_data)

    def send_from_sr(self, sr: str, to: str, subject: str, body: str) -> None:
        req_data = {
            'from_sr': sr,
            'to': to,
            'subject': subject,
            'text': body,
        }
        self._client.request('POST', '/api/compose', data=req_data)

    def reply(self, idn: int, body: str) -> ComposedMessage:
        data = {
            'thing_id': 't4_' + to_base36(idn),
            'text': body,
            'return_rtjson': '1',
        }
        result = self._client.request('POST', '/api/comment', data=data)
        root = result['json']['data']['things'][0]['data']
        return load_composed_message(root, self._client)

    def delete(self, idn: int) -> None:
        self._client.request('POST', '/api/del_msg', data={'id': 't4_' + to_base36(idn)})

    def mark_read(self, idn: int) -> None:
        self._client.request('POST', '/api/read_message', data={'id': 't4_' + to_base36(idn)})

    def mark_unread(self, idn: int) -> None:
        self._client.request('POST', '/api/unread_message', data={'id': 't4_' + to_base36(idn)})

    def mark_all_read(self) -> None:
        self._client.request('POST', '/api/read_all_messages')

    def mark_comment_read(self, idn: int) -> None:
        self._client.request('POST', '/api/read_message', data={'id': 't1_' + to_base36(idn)})

    def mark_comment_unread(self, idn: int) -> None:
        self._client.request('POST', '/api/read_message', data={'id': 't1_' + to_base36(idn)})

    def collapse(self, idn: int) -> None:
        self._client.request('POST', '/api/collapse_message', data={'id': 't4_' + to_base36(idn)})

    def uncollapse(self, idn: int) -> None:
        self._client.request('POST', '/api/uncollapse_message', data={'id': 't4_' + to_base36(idn)})

    class _block_author:
        def __init__(self, outer: Message) -> None:
            self._client = outer._client

        def __call__(self, idn: int) -> None:
            self.of_message(idn)

        def of_message(self, idn: int) -> None:
            self._client.request('POST', '/api/block', data={'id': 't4_' + to_base36(idn)})

        def of_comment(self, idn: int) -> None:
            self._client.request('POST', '/api/block', data={'id': 't1_' + to_base36(idn)})

        def of_submission(self, idn: int) -> None:
            self._client.request('POST', '/api/block', data={'id': 't3_' + to_base36(idn)})

    block_author = cached_property(_block_author)
