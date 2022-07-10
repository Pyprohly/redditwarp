
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.subreddit_user_item import (
        ModeratorUserItem,
        ApprovedUserItem,
        BannedUserItem,
        MutedUserItem,
    )

from ...pagination.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...pagination.paginators.moderation.async1 import (
    ModeratorsAsyncPaginator,
    ApprovedUsersAsyncPaginator,
    BannedUsersAsyncPaginator,
    MutedUsersAsyncPaginator,
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

    def approved_users(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[ApprovedUsersAsyncPaginator, ApprovedUserItem]:
        p = ApprovedUsersAsyncPaginator(self._client, f'/api/v1/{sr}/contributors')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[BannedUsersAsyncPaginator, BannedUserItem]:
        p = BannedUsersAsyncPaginator(self._client, f'/api/v1/{sr}/banned')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingAsyncIterator[MutedUsersAsyncPaginator, MutedUserItem]:
        p = MutedUsersAsyncPaginator(self._client, f'/api/v1/{sr}/muted')
        return ImpartedPaginatorChainingAsyncIterator(p, amount)
