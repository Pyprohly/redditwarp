
from __future__ import annotations
from typing import Sequence

from .listing.listing_async_paginator import ListingAsyncPaginator
from ...models.message_ASYNC import MailboxMessage, ComposedMessage, CommentMessage
from ...model_loaders.message_ASYNC import (
    load_message,
    load_composed_message,
    load_comment_message,
    load_composed_message_thread,
)

class MessageListingAsyncPaginator(ListingAsyncPaginator[MailboxMessage]):
    async def fetch(self) -> Sequence[MailboxMessage]:
        data = await self._fetch_data()
        return [load_message(d['data'], self.client) for d in data['children']]

class ComposedMessageListingAsyncPaginator(ListingAsyncPaginator[ComposedMessage]):
    async def fetch(self) -> Sequence[ComposedMessage]:
        data = await self._fetch_data()
        return [load_composed_message(d['data'], self.client) for d in data['children']]

class CommentMessageListingAsyncPaginator(ListingAsyncPaginator[CommentMessage]):
    async def fetch(self) -> Sequence[CommentMessage]:
        data = await self._fetch_data()
        return [load_comment_message(d['data'], self.client) for d in data['children']]

class ComposedMessageThreadListingAsyncPaginator(ListingAsyncPaginator[Sequence[ComposedMessage]]):
    async def fetch(self) -> Sequence[Sequence[ComposedMessage]]:
        data = await self._fetch_data()
        return [load_composed_message_thread(d['data'], self.client) for d in data['children']]
