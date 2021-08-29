
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_user_item import (
        ModeratorUserItem,
        ContributorUserItem,
        BannedUserItem,
        MutedUserItem,
    )

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator
from ...paginators.implementations.subreddit_pull_users_sync import (
    ModeratorsPaginator,
    ContributorsPaginator,
    BannedPaginator,
    MutedPaginator,
)

class PullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def moderators(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators')
        return PaginatorChainingIterator(p, amount)

    def moderator_invitations(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_invited')
        return PaginatorChainingIterator(p, amount)

    def editable_moderators(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_editable')
        return PaginatorChainingIterator(p, amount)

    def contributors(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[ContributorsPaginator, ContributorUserItem]:
        p = ContributorsPaginator(self._client, f'/api/v1/{sr}/contributors')
        return PaginatorChainingIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[BannedPaginator, BannedUserItem]:
        p = BannedPaginator(self._client, f'/api/v1/{sr}/banned')
        return PaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingIterator[MutedPaginator, MutedUserItem]:
        p = MutedPaginator(self._client, f'/api/v1/{sr}/muted')
        return PaginatorChainingIterator(p, amount)
