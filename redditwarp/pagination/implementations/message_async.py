
from __future__ import annotations
from typing import Sequence

from ..listing.listing_async_paginator import ListingAsyncPaginator
from ...models.message_ASYNC import Message, ComposedMessage, CommentMessage
from ...models.load.message_ASYNC import (
    load_message,
    load_composed_message,
    load_comment_message,
    load_threaded_message,
)

class MessageListingAsyncPaginator(ListingAsyncPaginator[Message]):
    async def fetch(self) -> Sequence[Message]:
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

class ThreadedMessagesListingAsyncPaginator(ListingAsyncPaginator[Sequence[ComposedMessage]]):
    async def fetch(self) -> Sequence[Sequence[ComposedMessage]]:
        data = await self._fetch_data()
        return [load_threaded_message(d['data'], self.client) for d in data['children']]
