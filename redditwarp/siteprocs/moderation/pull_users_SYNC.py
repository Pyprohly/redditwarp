
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

from ...paginators.paginator_chaining_iterator import PaginatorChainingIterator, PaginatorChainingWrapper
from ...paginators.implementations.subreddit_pull_users_sync import (
    ModeratorsPaginator,
    ContributorsPaginator,
    BannedPaginator,
    MutedPaginator,
)

class PullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def moderators(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingWrapper[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def moderator_invitations(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingWrapper[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_invited')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def editable_moderators(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingWrapper[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_editable')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def contributors(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingWrapper[ContributorsPaginator, ContributorUserItem]:
        p = ContributorsPaginator(self._client, f'/api/v1/{sr}/contributors')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def banned(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingWrapper[BannedPaginator, BannedUserItem]:
        p = BannedPaginator(self._client, f'/api/v1/{sr}/banned')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)

    def muted(self, sr: str, amount: Optional[int] = None) -> PaginatorChainingWrapper[MutedPaginator, MutedUserItem]:
        p = MutedPaginator(self._client, f'/api/v1/{sr}/muted')
        return PaginatorChainingWrapper(PaginatorChainingIterator(p, amount), p)
