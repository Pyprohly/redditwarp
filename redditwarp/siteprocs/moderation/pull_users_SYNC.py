
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_user_item import (
        ModeratorUserItem,
        ApprovedUserItem,
        BannedUserItem,
        MutedUserItem,
    )

from ...pagination.paginator_chaining_iterator import ImpartedPaginatorChainingIterator
from ...pagination.paginators.moderation.sync1 import (
    ModeratorsPaginator,
    ApprovedUsersPaginator,
    BannedUsersPaginator,
    MutedUsersPaginator,
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

    def approved_users(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ApprovedUsersPaginator, ApprovedUserItem]:
        p = ApprovedUsersPaginator(self._client, f'/api/v1/{sr}/contributors')
        return ImpartedPaginatorChainingIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[BannedUsersPaginator, BannedUserItem]:
        p = BannedUsersPaginator(self._client, f'/api/v1/{sr}/banned')
        return ImpartedPaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[MutedUsersPaginator, MutedUserItem]:
        p = MutedUsersPaginator(self._client, f'/api/v1/{sr}/muted')
        return ImpartedPaginatorChainingIterator(p, amount)
