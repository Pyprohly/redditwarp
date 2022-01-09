
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_user_item import (
        ModeratorUserItem,
        ContributorUserItem,
        BannedUserItem,
        MutedUserItem,
    )

from ...paginators.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...paginators.implementations.moderation._async_ import (
    ModeratorsAsyncPaginator,
    ContributorsAsyncPaginator,
    BannedAsyncPaginator,
    MutedAsyncPaginator,
)

class PullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def moderators(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ModeratorsAsyncPaginator, ModeratorUserItem]:
        p = ModeratorsAsyncPaginator(self._client, f'/api/v1/{sr}/moderators')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def moderator_invitations(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ModeratorsAsyncPaginator, ModeratorUserItem]:
        p = ModeratorsAsyncPaginator(self._client, f'/api/v1/{sr}/moderators_invited')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def editable_moderators(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ModeratorsAsyncPaginator, ModeratorUserItem]:
        p = ModeratorsAsyncPaginator(self._client, f'/api/v1/{sr}/moderators_editable')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def contributors(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ContributorsAsyncPaginator, ContributorUserItem]:
        p = ContributorsAsyncPaginator(self._client, f'/api/v1/{sr}/contributors')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[BannedAsyncPaginator, BannedUserItem]:
        p = BannedAsyncPaginator(self._client, f'/api/v1/{sr}/banned')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[MutedAsyncPaginator, MutedUserItem]:
        p = MutedAsyncPaginator(self._client, f'/api/v1/{sr}/muted')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
