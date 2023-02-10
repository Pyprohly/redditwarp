
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence, Iterable, Any
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ...async_paginator import HasMoreAsyncPaginator, Bidirectional, CursorAsyncPaginator
from ....models.subreddit_user import (
    Moderator,
    ApprovedUser,
    BannedUser,
    MutedUser,
)
from ....model_loaders.subreddit_user import (
    load_moderator,
    load_approved_user,
    load_banned_user,
    load_muted_user,
)

T = TypeVar('T')

class ModerationUsersAsyncPaginator(HasMoreAsyncPaginator[T], Bidirectional, CursorAsyncPaginator[T]):
    def __init__(self,
        client: Client,
        url: str,
        *,
        limit: Optional[int] = 100,
    ) -> None:
        super().__init__(limit=limit)
        self.direction: bool = True
        self.client: Client = client
        self.url: str = url
        self._after: str = ''
        self._before: str = ''
        self._has_after: bool = True
        self._has_before: bool = True

    def get_cursor(self) -> str:
        return self._after if self.direction else self._before

    def set_cursor(self, value: str) -> None:
        if self.direction:
            self._after = value
        else:
            self._before = value

    def has_more(self) -> bool:
        return self._has_after if self.direction else self._has_before

    def set_has_more(self, value: bool) -> None:
        if self.direction:
            self._has_after = value
        else:
            self._has_before = value

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        if self.limit is not None:
            yield ('count', str(self.limit))

        if self.direction:
            if self._after:
                yield ('after', self._after)
        else:
            if self._before:
                yield ('before', self._before)

    async def _fetch_data(self) -> Any:
        params = dict(self._generate_params())
        root = await self.client.request('GET', self.url, params=params)
        after = root['after'] or ''
        before = root['before'] or ''
        self._after = after
        self._before = before
        self._has_after = bool(after)
        self._has_before = bool(before)
        return root


class ModeratorsAsyncPaginator(ModerationUsersAsyncPaginator[Moderator]):
    async def fetch(self) -> Sequence[Moderator]:
        root = await self._fetch_data()
        order = root['moderatorIds']
        object_map = root['moderators']
        return [load_moderator(object_map[full_id36]) for full_id36 in order]

class ApprovedUsersAsyncPaginator(ModerationUsersAsyncPaginator[ApprovedUser]):
    async def fetch(self) -> Sequence[ApprovedUser]:
        root = await self._fetch_data()
        order = root['approvedSubmitterIds']
        object_map = root['approvedSubmitters']
        return [load_approved_user(object_map[full_id36]) for full_id36 in order]

class BannedUsersAsyncPaginator(ModerationUsersAsyncPaginator[BannedUser]):
    async def fetch(self) -> Sequence[BannedUser]:
        root = await self._fetch_data()
        order = root['bannedUserIds']
        object_map = root['bannedUsers']
        return [load_banned_user(object_map[full_id36]) for full_id36 in order]

class MutedUsersAsyncPaginator(ModerationUsersAsyncPaginator[MutedUser]):
    async def fetch(self) -> Sequence[MutedUser]:
        root = await self._fetch_data()
        order = root['mutedUserIds']
        object_map = root['mutedUsers']
        return [load_muted_user(object_map[full_id36]) for full_id36 in order]
