
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import Message, ComposedMessage, CommentMessage

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.listing.p_mailbox_message_listing_paginator import (
    MessageListingPaginator,
    ComposedMessageListingPaginator,
    CommentMessageListingPaginator,
    ThreadedMessagesListingPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[MessageListingPaginator, Message]:
        return self.inbox(amount)

    def inbox(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[MessageListingPaginator, Message]:
        p = MessageListingPaginator(self._client, '/message/inbox')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def unread(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[MessageListingPaginator, Message]:
        p = MessageListingPaginator(self._client, '/message/unread')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def messages(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[ThreadedMessagesListingPaginator, Sequence[ComposedMessage]]:
        p = ThreadedMessagesListingPaginator(self._client, '/message/messages')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def sent(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[ComposedMessageListingPaginator, ComposedMessage]:
        p = ComposedMessageListingPaginator(self._client, '/message/sent')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def comment_replies(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/comments')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def post_replies(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/selfreply')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def mentions(self, amount: Optional[int] = None) -> PaginatorChainingWrapper[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/mentions')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
