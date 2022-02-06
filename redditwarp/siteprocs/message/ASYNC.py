
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.message_ASYNC import ComposedMessage

from functools import cached_property

from ...util.base_conversion import to_base36
from ...models.load.message_ASYNC import load_composed_message
from .get_ASYNC import Get
from .fetch_ASYNC import Fetch
from .pull_ASYNC import Pull

class MessageProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.get: Get = Get(self, client)
        self.fetch: Fetch = Fetch(client)
        self.pull: Pull = Pull(client)

    async def send(self, to: str, subject: str, body: str) -> None:
        req_data = {
            'to': to,
            'subject': subject,
            'text': body,
        }
        await self._client.request('POST', '/api/compose', data=req_data)

    async def send_from_sr(self, sr: str, to: str, subject: str, body: str) -> None:
        req_data = {
            'from_sr': sr,
            'to': to,
            'subject': subject,
            'text': body,
        }
        await self._client.request('POST', '/api/compose', data=req_data)

    async def reply(self, idn: int, body: str) -> ComposedMessage:
        data = {
            'thing_id': 't4_' + to_base36(idn),
            'text': body,
            'return_rtjson': '1',
        }
        result = await self._client.request('POST', '/api/comment', data=data)
        root = result['json']['data']['things'][0]['data']
        return load_composed_message(root, self._client)

    async def delete(self, idn: int) -> None:
        await self._client.request('POST', '/api/del_msg', data={'id': 't4_' + to_base36(idn)})

    async def mark_read(self, idn: int) -> None:
        await self._client.request('POST', '/api/read_message', data={'id': 't4_' + to_base36(idn)})

    async def mark_unread(self, idn: int) -> None:
        await self._client.request('POST', '/api/unread_message', data={'id': 't4_' + to_base36(idn)})

    async def mark_all_read(self) -> None:
        await self._client.request('POST', '/api/read_all_messages')

    async def mark_comment_read(self, idn: int) -> None:
        await self._client.request('POST', '/api/read_message', data={'id': 't1_' + to_base36(idn)})

    async def mark_comment_unread(self, idn: int) -> None:
        await self._client.request('POST', '/api/read_message', data={'id': 't1_' + to_base36(idn)})

    async def collapse(self, idn: int) -> None:
        await self._client.request('POST', '/api/collapse_message', data={'id': 't4_' + to_base36(idn)})

    async def uncollapse(self, idn: int) -> None:
        await self._client.request('POST', '/api/uncollapse_message', data={'id': 't4_' + to_base36(idn)})

    class _block_author:
        def __init__(self, outer: MessageProcedures) -> None:
            self._client = outer._client

        async def __call__(self, idn: int) -> None:
            await self.of_message(idn)

        async def of_message(self, idn: int) -> None:
            await self._client.request('POST', '/api/block', data={'id': 't4_' + to_base36(idn)})

        async def of_comment(self, idn: int) -> None:
            await self._client.request('POST', '/api/block', data={'id': 't1_' + to_base36(idn)})

        async def of_submission(self, idn: int) -> None:
            await self._client.request('POST', '/api/block', data={'id': 't3_' + to_base36(idn)})

    block_author: cached_property[_block_author] = cached_property(_block_author)
