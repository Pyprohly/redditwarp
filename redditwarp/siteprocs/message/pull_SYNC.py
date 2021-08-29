
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import MailboxMessage, ComposedMessage, CommentMessage

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.listing.mailbox_message_listing_paginator import (
    MailboxMessageListingPaginator,
    ComposedMessageListingPaginator,
    CommentMessageListingPaginator,
    ThreadedMessagesListingPaginator,
)
from ...util.tree_node import GeneralTreeNode

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None) -> PaginatorChainingIterator[MailboxMessageListingPaginator, MailboxMessage]:
        return self.inbox(amount)

    def inbox(self, amount: Optional[int] = None) -> PaginatorChainingIterator[MailboxMessageListingPaginator, MailboxMessage]:
        p = MailboxMessageListingPaginator(self._client, '/message/inbox')
        return PaginatorChainingIterator(p, amount)

    def unread(self, amount: Optional[int] = None) -> PaginatorChainingIterator[MailboxMessageListingPaginator, MailboxMessage]:
        p = MailboxMessageListingPaginator(self._client, '/message/unread')
        return PaginatorChainingIterator(p, amount)

    def messages(self, amount: Optional[int] = None) -> PaginatorChainingIterator[ThreadedMessagesListingPaginator, GeneralTreeNode[MailboxMessage, MailboxMessage]]:
        p = ThreadedMessagesListingPaginator(self._client, '/message/messages')
        return PaginatorChainingIterator(p, amount)

    def sent(self, amount: Optional[int] = None) -> PaginatorChainingIterator[ComposedMessageListingPaginator, ComposedMessage]:
        p = ComposedMessageListingPaginator(self._client, '/message/sent')
        return PaginatorChainingIterator(p, amount)

    def comment_replies(self, amount: Optional[int] = None) -> PaginatorChainingIterator[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/comments')
        return PaginatorChainingIterator(p, amount)

    def post_replies(self, amount: Optional[int] = None) -> PaginatorChainingIterator[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/selfreply')
        return PaginatorChainingIterator(p, amount)

    def mentions(self, amount: Optional[int] = None) -> PaginatorChainingIterator[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/mentions')
        return PaginatorChainingIterator(p, amount)
