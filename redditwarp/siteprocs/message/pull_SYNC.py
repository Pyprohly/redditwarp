
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.message_SYNC import MailboxMessage, ComposedMessage, CommentMessage

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.message_sync1 import (
    MessageListingPaginator,
    ComposedMessageListingPaginator,
    CommentMessageListingPaginator,
    ComposedMessageThreadListingPaginator,
)

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def inbox(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[MessageListingPaginator, MailboxMessage]:
        p = MessageListingPaginator(self._client, '/message/inbox')
        return ImpartedPaginatorChainingIterator(p, amount)

    def unread(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[MessageListingPaginator, MailboxMessage]:
        p = MessageListingPaginator(self._client, '/message/unread')
        return ImpartedPaginatorChainingIterator(p, amount)

    def messages(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ComposedMessageThreadListingPaginator, Sequence[ComposedMessage]]:
        p = ComposedMessageThreadListingPaginator(self._client, '/message/messages')
        return ImpartedPaginatorChainingIterator(p, amount)

    def sent(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ComposedMessageListingPaginator, ComposedMessage]:
        p = ComposedMessageListingPaginator(self._client, '/message/sent')
        return ImpartedPaginatorChainingIterator(p, amount)

    def comment_replies(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/comments')
        return ImpartedPaginatorChainingIterator(p, amount)

    def post_replies(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/selfreply')
        return ImpartedPaginatorChainingIterator(p, amount)

    def mentions(self, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[CommentMessageListingPaginator, CommentMessage]:
        p = CommentMessageListingPaginator(self._client, '/message/mentions')
        return ImpartedPaginatorChainingIterator(p, amount)
