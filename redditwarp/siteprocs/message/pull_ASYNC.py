
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.message_ASYNC import MailboxMessage, ComposedMessage, CommentMessage

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.implementations.message_async import (
    MessageListingAsyncPaginator,
    ComposedMessageListingAsyncPaginator,
    CommentMessageListingAsyncPaginator,
    ComposedMessageThreadListingAsyncPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[MessageListingAsyncPaginator, MailboxMessage]:
        return self.inbox(amount)

    def inbox(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[MessageListingAsyncPaginator, MailboxMessage]:
        p = MessageListingAsyncPaginator(self._client, '/message/inbox')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def unread(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[MessageListingAsyncPaginator, MailboxMessage]:
        p = MessageListingAsyncPaginator(self._client, '/message/unread')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def messages(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ComposedMessageThreadListingAsyncPaginator, Sequence[ComposedMessage]]:
        p = ComposedMessageThreadListingAsyncPaginator(self._client, '/message/messages')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def sent(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ComposedMessageListingAsyncPaginator, ComposedMessage]:
        p = ComposedMessageListingAsyncPaginator(self._client, '/message/sent')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def comment_replies(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[CommentMessageListingAsyncPaginator, CommentMessage]:
        p = CommentMessageListingAsyncPaginator(self._client, '/message/comments')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def post_replies(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[CommentMessageListingAsyncPaginator, CommentMessage]:
        p = CommentMessageListingAsyncPaginator(self._client, '/message/selfreply')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def mentions(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[CommentMessageListingAsyncPaginator, CommentMessage]:
        p = CommentMessageListingAsyncPaginator(self._client, '/message/mentions')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
