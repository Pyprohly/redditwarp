
from __future__ import annotations
from typing import Sequence

from .listing_paginator import ListingPaginator
from ....util.tree_node import GeneralTreeNode
from ....models.message_SYNC import MailboxMessage, ComposedMessage, CommentMessage
from ....models.load.message_SYNC import (
    load_mailbox_message,
    load_composed_message,
    load_comment_message,
    load_threaded_message,
)

class MailboxMessageListingPaginator(ListingPaginator[MailboxMessage]):
    def next_result(self) -> Sequence[MailboxMessage]:
        data = self._next_data()
        return [load_mailbox_message(d['data'], self.client) for d in data['children']]

class ComposedMessageListingPaginator(ListingPaginator[ComposedMessage]):
    def next_result(self) -> Sequence[ComposedMessage]:
        data = self._next_data()
        return [load_composed_message(d['data'], self.client) for d in data['children']]

class CommentMessageListingPaginator(ListingPaginator[CommentMessage]):
    def next_result(self) -> Sequence[CommentMessage]:
        data = self._next_data()
        return [load_comment_message(d['data'], self.client) for d in data['children']]

class ThreadedMessagesListingPaginator(ListingPaginator[GeneralTreeNode[MailboxMessage, MailboxMessage]]):
    def next_result(self) -> Sequence[GeneralTreeNode[MailboxMessage, MailboxMessage]]:
        data = self._next_data()
        return [load_threaded_message(d['data'], self.client) for d in data['children']]
