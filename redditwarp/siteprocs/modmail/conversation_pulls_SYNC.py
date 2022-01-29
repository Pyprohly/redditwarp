
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.modmail_SYNC import Conversation, Message

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.implementations.modmail_sync import ModmailConversationsPaginator

class Pulls:
    def __init__(self, client: Client) -> None:
        self._client = client

    def __call__(self,
        mailbox: str,
        amount: Optional[int] = None,
        *,
        subreddit_names: Sequence[str] = (),
        sort: str = '',
    ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        p = ModmailConversationsPaginator(self._client, '/api/mod/conversations', mailbox, subreddit_names, sort)
        return ImpartedPaginatorChainingIterator(p, amount)

    def all(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('all', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def inbox(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('inbox', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def new(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('new', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def in_progress(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('inprogress', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def archived(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('archived', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def appeals(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('appeals', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def join_requests(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('join_requests', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def highlighted(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('highlighted', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def mod(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('mod', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def notifications(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationsPaginator, tuple[Conversation, Message]]:
        return self('notifications', amount=amount, subreddit_names=subreddit_names, sort=sort)
