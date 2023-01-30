
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence, Iterable, Any
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ...paginator import HasMorePaginator, Bidirectional, CursorPaginator
from ....models.subreddit_user_item import (
    ModeratorUserItem,
    ApprovedUserItem,
    BannedUserItem,
    MutedUserItem,
)
from ....model_loaders.subreddit_user_item import (
    load_moderator_user_item,
    load_approved_user_item,
    load_banned_user_item,
    load_muted_user_item,
)

T = TypeVar('T')

class ModerationUsersPaginator(HasMorePaginator[T], Bidirectional, CursorPaginator[T]):
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

    def _fetch_data(self) -> Any:
        params = dict(self._generate_params())
        root = self.client.request('GET', self.url, params=params)
        after = root['after'] or ''
        before = root['before'] or ''
        self._after = after
        self._before = before
        self._has_after = bool(after)
        self._has_before = bool(before)
        return root


class ModeratorsPaginator(ModerationUsersPaginator[ModeratorUserItem]):
    def fetch(self) -> Sequence[ModeratorUserItem]:
        root = self._fetch_data()
        order = root['moderatorIds']
        object_map = root['moderators']
        return [load_moderator_user_item(object_map[full_id36]) for full_id36 in order]

class ApprovedUsersPaginator(ModerationUsersPaginator[ApprovedUserItem]):
    def fetch(self) -> Sequence[ApprovedUserItem]:
        root = self._fetch_data()
        order = root['approvedSubmitterIds']
        object_map = root['approvedSubmitters']
        return [load_approved_user_item(object_map[full_id36]) for full_id36 in order]

class BannedUsersPaginator(ModerationUsersPaginator[BannedUserItem]):
    def fetch(self) -> Sequence[BannedUserItem]:
        root = self._fetch_data()
        order = root['bannedUserIds']
        object_map = root['bannedUsers']
        return [load_banned_user_item(object_map[full_id36]) for full_id36 in order]

class MutedUsersPaginator(ModerationUsersPaginator[MutedUserItem]):
    def fetch(self) -> Sequence[MutedUserItem]:
        root = self._fetch_data()
        order = root['mutedUserIds']
        object_map = root['mutedUsers']
        return [load_muted_user_item(object_map[full_id36]) for full_id36 in order]
