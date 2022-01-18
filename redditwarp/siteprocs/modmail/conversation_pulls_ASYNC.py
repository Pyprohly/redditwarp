
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.modmail_ASYNC import Conversation, Message

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.implementations.modmail_async import ModmailConversationsAsyncPaginator

class Pulls:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self,
        mailbox: str,
        amount: Optional[int] = None,
        *,
        subreddit_names: Sequence[str] = (),
        sort: str = '',
    ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        p = ModmailConversationsAsyncPaginator(self._client, '/api/mod/conversations', mailbox, subreddit_names, sort)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def all(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('all', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def inbox(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('inbox', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def new(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('new', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def in_progress(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('inprogress', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def archived(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('archived', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def appeals(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('appeals', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def join_requests(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('join_requests', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def highlighted(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('highlighted', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def mod(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('mod', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def notifications(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingAsyncIterator[ModmailConversationsAsyncPaginator, tuple[Conversation, Message]]:
        return self.__call__('notifications', amount=amount, subreddit_names=subreddit_names, sort=sort)
