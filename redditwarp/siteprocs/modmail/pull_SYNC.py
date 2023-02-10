
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.modmail_SYNC import ConversationInfo, Message

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.modmail_sync1 import ModmailConversationMessagePaginator

class Pull:
    def __init__(self, client: Client) -> None:
        self._client = client

    def _mailbox(self,
        mailbox: str,
        amount: Optional[int] = None,
        *,
        subreddit_names: Sequence[str] = (),
        sort: str = '',
    ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        p = ModmailConversationMessagePaginator(self._client, '/api/mod/conversations', mailbox, subreddit_names, sort)
        return ImpartedPaginatorChainingIterator(p, amount)

    def all(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('all', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def inbox(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('inbox', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def new(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('new', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def in_progress(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('inprogress', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def archived(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('archived', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def filtered(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('filtered', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def appeals(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('appeals', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def join_requests(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('join_requests', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def highlighted(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('highlighted', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def mod(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('mod', amount=amount, subreddit_names=subreddit_names, sort=sort)

    def notifications(self, amount: Optional[int] = None, *, subreddit_names: Sequence[str] = (), sort: str = '',
            ) -> ImpartedPaginatorChainingIterator[ModmailConversationMessagePaginator, tuple[ConversationInfo, Message]]:
        return self._mailbox('notifications', amount=amount, subreddit_names=subreddit_names, sort=sort)
