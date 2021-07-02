
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....models.message_SYNC import MailboxMessage, ComposedMessage, CommentMessage
from ....models.load.message_SYNC import (
    load_mailbox_message,
    load_composed_message,
    load_comment_message,
)

class MailboxMessageListingPaginator(ListingPaginator[MailboxMessage]):
    def _fetch_result(self) -> Sequence[MailboxMessage]:
        data = self._fetch_data()
        return [load_mailbox_message(d['data'], self.client) for d in data['children']]

class ComposedMessageListingPaginator(ListingPaginator[ComposedMessage]):
    def _fetch_result(self) -> Sequence[ComposedMessage]:
        data = self._fetch_data()
        return [load_composed_message(d['data'], self.client) for d in data['children']]

class CommentMessageListingPaginator(ListingPaginator[CommentMessage]):
    def _fetch_result(self) -> Sequence[CommentMessage]:
        data = self._fetch_data()
        return [load_comment_message(d['data'], self.client) for d in data['children']]
