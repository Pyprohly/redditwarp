
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Sequence, Iterable, Optional, Mapping, Any
if TYPE_CHECKING:
    from ...client_SYNC import Client

from ..bidirectional_cursor_paginator import BidirectionalCursorPaginator
from ..exceptions import MissingCursorException
from ...models.subreddit_user_item import (
    ModeratorUserItem,
    ContributorUserItem,
    BannedUserItem,
    MutedUserItem,
)
from ...models.load.subreddit_user_item import (
    load_moderator_user_item,
    load_contributor_user_item,
    load_banned_user_item,
    load_muted_user_item,
)


T = TypeVar('T')

class ModerationPullUsersPaginator(BidirectionalCursorPaginator[T]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 100,
    ):
        super().__init__()
        self.client = client
        self.uri = uri

    def _generate_params(self) -> Iterable[tuple[str, Optional[str]]]:
        if self.limit is not None:
            yield ('count', str(self.limit))
        if self.direction:
            if not self.after and not self.has_after:
                raise MissingCursorException('after')
            yield ('after', self.after)
        else:
            if not self.before and not self.has_before:
                raise MissingCursorException('before')
            yield ('before', self.before)

    def _fetch_data(self) -> Mapping[str, Any]:
        params = dict(self._generate_params())
        root = self.client.request('GET', self.uri, params=params)
        after = root['after'] or ''
        before = root['before'] or ''
        self.after = after
        self.before = before
        self.has_after = bool(after)
        self.has_before = bool(before)
        return root


class ModeratorsPaginator(ModerationPullUsersPaginator[ModeratorUserItem]):
    def fetch_next_result(self) -> Sequence[ModeratorUserItem]:
        root = self._fetch_data()
        sequence = root['moderatorIds']
        object_mapping = root['moderators']
        return [load_moderator_user_item(object_mapping[full_id36]) for full_id36 in sequence]

class ContributorsPaginator(ModerationPullUsersPaginator[ContributorUserItem]):
    def fetch_next_result(self) -> Sequence[ContributorUserItem]:
        root = self._fetch_data()
        sequence = root['approvedSubmitterIds']
        object_mapping = root['approvedSubmitters']
        return [load_contributor_user_item(object_mapping[full_id36]) for full_id36 in sequence]

class BannedPaginator(ModerationPullUsersPaginator[BannedUserItem]):
    def fetch_next_result(self) -> Sequence[BannedUserItem]:
        root = self._fetch_data()
        sequence = root['bannedUserIds']
        object_mapping = root['bannedUsers']
        return [load_banned_user_item(object_mapping[full_id36]) for full_id36 in sequence]

class MutedPaginator(ModerationPullUsersPaginator[MutedUserItem]):
    def fetch_next_result(self) -> Sequence[MutedUserItem]:
        root = self._fetch_data()
        sequence = root['mutedUserIds']
        object_mapping = root['mutedUsers']
        return [load_muted_user_item(object_mapping[full_id36]) for full_id36 in sequence]
