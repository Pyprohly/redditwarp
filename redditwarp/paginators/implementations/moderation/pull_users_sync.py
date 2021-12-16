
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence, Iterable, Mapping, Any
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...bidirectional_cursor_paginator import BidirectionalCursorPaginator
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

class ModerationUsersPaginator(BidirectionalCursorPaginator[T]):
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

    def _fetch_next_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        root = self.client.request('GET', self.uri, params=params)
        after = root['after'] or ''
        before = root['before'] or ''
        self.after: str = after
        self.before: str = before
        self.has_after: bool = bool(after)
        self.has_before: bool = bool(before)
        return root


class ModeratorsPaginator(ModerationUsersPaginator[ModeratorUserItem]):
    def fetch_next(self) -> Sequence[ModeratorUserItem]:
        root = self._fetch_next_data()
        order = root['moderatorIds']
        object_map = root['moderators']
        return [load_moderator_user_item(object_map[full_id36]) for full_id36 in order]

class ContributorsPaginator(ModerationUsersPaginator[ContributorUserItem]):
    def fetch_next(self) -> Sequence[ContributorUserItem]:
        root = self._fetch_next_data()
        order = root['approvedSubmitterIds']
        object_map = root['approvedSubmitters']
        return [load_contributor_user_item(object_map[full_id36]) for full_id36 in order]

class BannedPaginator(ModerationUsersPaginator[BannedUserItem]):
    def fetch_next(self) -> Sequence[BannedUserItem]:
        root = self._fetch_next_data()
        order = root['bannedUserIds']
        object_map = root['bannedUsers']
        return [load_banned_user_item(object_map[full_id36]) for full_id36 in order]

class MutedPaginator(ModerationUsersPaginator[MutedUserItem]):
    def fetch_next(self) -> Sequence[MutedUserItem]:
        root = self._fetch_next_data()
        order = root['mutedUserIds']
        object_map = root['mutedUsers']
        return [load_muted_user_item(object_map[full_id36]) for full_id36 in order]
