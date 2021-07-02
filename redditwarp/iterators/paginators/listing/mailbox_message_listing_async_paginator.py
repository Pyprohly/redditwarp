
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....models.message_ASYNC import MailboxMessage, ComposedMessage, CommentMessage
from ....models.load.message_ASYNC import (
    load_mailbox_message,
    load_composed_message,
    load_comment_message,
)

class MailboxMessageListingAsyncPaginator(ListingAsyncPaginator[MailboxMessage]):
    async def _fetch_result(self) -> Sequence[MailboxMessage]:
        data = await self._fetch_data()
        return [load_mailbox_message(d['data'], self.client) for d in data['children']]

class ComposedMessageListingAsyncPaginator(ListingAsyncPaginator[ComposedMessage]):
    async def _fetch_result(self) -> Sequence[ComposedMessage]:
        data = await self._fetch_data()
        return [load_composed_message(d['data'], self.client) for d in data['children']]

class CommentMessageListingAsyncPaginator(ListingAsyncPaginator[CommentMessage]):
    async def _fetch_result(self) -> Sequence[CommentMessage]:
        data = await self._fetch_data()
        return [load_comment_message(d['data'], self.client) for d in data['children']]
