
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

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.implementations.moderation.sync import (
    ModeratorsPaginator,
    ContributorsPaginator,
    BannedPaginator,
    MutedPaginator,
)

class PullUsers:
    def __init__(self, client: Client) -> None:
        self._client = client

    def moderators(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators')
        return ImpartedPaginatorChainingIterator(p, amount)

    def moderator_invitations(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_invited')
        return ImpartedPaginatorChainingIterator(p, amount)

    def editable_moderators(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ModeratorsPaginator, ModeratorUserItem]:
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_editable')
        return ImpartedPaginatorChainingIterator(p, amount)

    def contributors(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ContributorsPaginator, ContributorUserItem]:
        p = ContributorsPaginator(self._client, f'/api/v1/{sr}/contributors')
        return ImpartedPaginatorChainingIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[BannedPaginator, BannedUserItem]:
        p = BannedPaginator(self._client, f'/api/v1/{sr}/banned')
        return ImpartedPaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[MutedPaginator, MutedUserItem]:
        p = MutedPaginator(self._client, f'/api/v1/{sr}/muted')
        return ImpartedPaginatorChainingIterator(p, amount)
