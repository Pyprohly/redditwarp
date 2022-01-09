
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence, Iterable, Mapping, Any
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ...bidirectional_cursor_async_paginator import BidirectionalCursorAsyncPaginator
from ...exceptions import MissingCursorException
from ....models.subreddit_user_item import (
    ModeratorUserItem,
    ContributorUserItem,
    BannedUserItem,
    MutedUserItem,
)
from ....models.load.subreddit_user_item import (
    load_moderator_user_item,
    load_contributor_user_item,
    load_banned_user_item,
    load_muted_user_item,
)

T = TypeVar('T')

class ModerationUsersAsyncPaginator(BidirectionalCursorAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
    ):
        super().__init__()
        self.client: Client = client
        self.uri: str = uri

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        if self.limit is not None:
            yield ('count', str(self.limit))

        if self.direction:
            if self.after:
                yield ('after', self.after)
            elif not self.has_after:
                raise MissingCursorException('after')
        else:
            if self.before:
                yield ('before', self.before)
            elif not self.has_before:
                raise MissingCursorException('before')

    async def _fetch_next_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        root = await self.client.request('GET', self.uri, params=params)
        after = root['after'] or ''
        before = root['before'] or ''
        self.after: str = after
        self.before: str = before
        self.has_after: bool = bool(after)
        self.has_before: bool = bool(before)
        return root


class ModeratorsAsyncPaginator(ModerationUsersAsyncPaginator[ModeratorUserItem]):
    async def fetch_next(self) -> Sequence[ModeratorUserItem]:
        root = await self._fetch_next_data()
        order = root['moderatorIds']
        object_map = root['moderators']
        return [load_moderator_user_item(object_map[full_id36]) for full_id36 in order]

class ContributorsAsyncPaginator(ModerationUsersAsyncPaginator[ContributorUserItem]):
    async def fetch_next(self) -> Sequence[ContributorUserItem]:
        root = await self._fetch_next_data()
        order = root['approvedSubmitterIds']
        object_map = root['approvedSubmitters']
        return [load_contributor_user_item(object_map[full_id36]) for full_id36 in order]

class BannedAsyncPaginator(ModerationUsersAsyncPaginator[BannedUserItem]):
    async def fetch_next(self) -> Sequence[BannedUserItem]:
        root = await self._fetch_next_data()
        order = root['bannedUserIds']
        object_map = root['bannedUsers']
        return [load_banned_user_item(object_map[full_id36]) for full_id36 in order]

class MutedAsyncPaginator(ModerationUsersAsyncPaginator[MutedUserItem]):
    async def fetch_next(self) -> Sequence[MutedUserItem]:
        root = await self._fetch_next_data()
        order = root['mutedUserIds']
        object_map = root['mutedUsers']
        return [load_muted_user_item(object_map[full_id36]) for full_id36 in order]
