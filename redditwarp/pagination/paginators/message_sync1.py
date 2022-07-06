
from __future__ import annotations
from typing import Sequence

from .listing.listing_paginator import ListingPaginator
from ...models.message_SYNC import MailboxMessage, ComposedMessage, CommentMessage
from ...model_loaders.message_SYNC import (
    load_mailbox_message,
    load_composed_message,
    load_comment_message,
    load_composed_message_thread,
)

class MessageListingPaginator(ListingPaginator[MailboxMessage]):
    def fetch(self) -> Sequence[MailboxMessage]:
        data = self._fetch_data()
        return [load_mailbox_message(d['data'], self.client) for d in data['children']]

class ComposedMessageListingPaginator(ListingPaginator[ComposedMessage]):
    def fetch(self) -> Sequence[ComposedMessage]:
        data = self._fetch_data()
        return [load_composed_message(d['data'], self.client) for d in data['children']]

class CommentMessageListingPaginator(ListingPaginator[CommentMessage]):
    def fetch(self) -> Sequence[CommentMessage]:
        data = self._fetch_data()
        return [load_comment_message(d['data'], self.client) for d in data['children']]

class ComposedMessageThreadListingPaginator(ListingPaginator[Sequence[ComposedMessage]]):
    def fetch(self) -> Sequence[Sequence[ComposedMessage]]:
        data = self._fetch_data()
        return [load_composed_message_thread(d['data'], self.client) for d in data['children']]
