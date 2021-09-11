
from __future__ import annotations
from typing import Sequence

from .listing_async_paginator import ListingAsyncPaginator
from ....util.tree_node import GeneralTreeNode
from ....models.message_ASYNC import MailboxMessage, ComposedMessage, CommentMessage
from ....models.load.message_ASYNC import (
    load_mailbox_message,
    load_composed_message,
    load_comment_message,
    load_threaded_message,
)

class MailboxMessageListingAsyncPaginator(ListingAsyncPaginator[MailboxMessage]):
    async def next_result(self) -> Sequence[MailboxMessage]:
        data = await self._next_data()
        return [load_mailbox_message(d['data'], self.client) for d in data['children']]

class ComposedMessageListingAsyncPaginator(ListingAsyncPaginator[ComposedMessage]):
    async def next_result(self) -> Sequence[ComposedMessage]:
        data = await self._next_data()
        return [load_composed_message(d['data'], self.client) for d in data['children']]

class CommentMessageListingAsyncPaginator(ListingAsyncPaginator[CommentMessage]):
    async def next_result(self) -> Sequence[CommentMessage]:
        data = await self._next_data()
        return [load_comment_message(d['data'], self.client) for d in data['children']]

class ThreadedMessagesListingAsyncPaginator(ListingAsyncPaginator[GeneralTreeNode[MailboxMessage, MailboxMessage]]):
    async def next_result(self) -> Sequence[GeneralTreeNode[MailboxMessage, MailboxMessage]]:
        data = await self._next_data()
        return [load_threaded_message(d['data'], self.client) for d in data['children']]
