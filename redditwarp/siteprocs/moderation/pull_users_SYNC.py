
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_user import (
        Moderator,
        ApprovedUser,
        BannedUser,
        MutedUser,
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

    def moderators(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ModeratorsPaginator, Moderator]:
        """
        Behaves similarly to :meth:`.approved_users`.
        """
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators')
        return ImpartedPaginatorChainingIterator(p, amount)

    def moderator_invitations(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ModeratorsPaginator, Moderator]:
        """
        Behaves similarly to :meth:`.approved_users`.
        """
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_invited')
        return ImpartedPaginatorChainingIterator(p, amount)

    def editable_moderators(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ModeratorsPaginator, Moderator]:
        """
        Behaves similarly to :meth:`.approved_users`.
        """
        p = ModeratorsPaginator(self._client, f'/api/v1/{sr}/moderators_editable')
        return ImpartedPaginatorChainingIterator(p, amount)

    def approved_users(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[ApprovedUsersPaginator, ApprovedUser]:
        """Get redditors that relate to a subreddit.

        .. .PARAMETERS

        :param `str` sr:
        :param `Optional[int]` amount:

        .. .RETURNS

        :rtype: :class:`~.pagination.paginator_chaining_iterator.ImpartedPaginatorChainingIterator`\\[:class:`~.pagination.paginators.moderation.sync1.ApprovedUsersPaginator`, :class:`~.models.subreddit_user.ApprovedUser`]

        .. .RAISES

        :raises redditwarp.exceptions.RedditError:
            + `SUBREDDIT_NOEXIST`:
                The target subreddit does not exist.
            + `SUBREDDIT_NO_ACCESS`:
                The subreddit cannot be accessed.
        :raises redditwarp.http.exceptions.StatusCodeException:
            + `403`:
                You don't have permission.
        """
        p = ApprovedUsersPaginator(self._client, f'/api/v1/{sr}/contributors')
        return ImpartedPaginatorChainingIterator(p, amount)

    def banned(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[BannedUsersPaginator, BannedUser]:
        """
        Behaves similarly to :meth:`.approved_users`.
        """
        p = BannedUsersPaginator(self._client, f'/api/v1/{sr}/banned')
        return ImpartedPaginatorChainingIterator(p, amount)

    def muted(self, sr: str, amount: Optional[int] = None) -> ImpartedPaginatorChainingIterator[MutedUsersPaginator, MutedUser]:
        """
        Behaves similarly to :meth:`.approved_users`.
        """
        p = MutedUsersPaginator(self._client, f'/api/v1/{sr}/muted')
        return ImpartedPaginatorChainingIterator(p, amount)
