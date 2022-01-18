
from __future__ import annotations
from typing import Sequence

from ..listing.listing_paginator import ListingPaginator
from ...models.message_SYNC import Message, ComposedMessage, CommentMessage
from ...models.load.message_SYNC import (
    load_message,
    load_composed_message,
    load_comment_message,
    load_threaded_message,
)

class MessageListingPaginator(ListingPaginator[Message]):
    def fetch(self) -> Sequence[Message]:
        data = self._fetch_data()
        return [load_message(d['data'], self.client) for d in data['children']]

class ComposedMessageListingPaginator(ListingPaginator[ComposedMessage]):
    def fetch(self) -> Sequence[ComposedMessage]:
        data = self._fetch_data()
        return [load_composed_message(d['data'], self.client) for d in data['children']]

class CommentMessageListingPaginator(ListingPaginator[CommentMessage]):
    def fetch(self) -> Sequence[CommentMessage]:
        data = self._fetch_data()
        return [load_comment_message(d['data'], self.client) for d in data['children']]

class ThreadedMessagesListingPaginator(ListingPaginator[Sequence[ComposedMessage]]):
    def fetch(self) -> Sequence[Sequence[ComposedMessage]]:
        data = self._fetch_data()
        return [load_threaded_message(d['data'], self.client) for d in data['children']]
