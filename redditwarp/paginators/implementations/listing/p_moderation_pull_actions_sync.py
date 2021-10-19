
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .listing_paginator import ListingPaginator
from ....models.moderation_action_log_entry import ModerationActionLogEntry
from ....models.load.moderation_action_log_entry import load_mod_log_action_entry

class ModerationActionLogPaginator(ListingPaginator[ModerationActionLogEntry]):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        limit: Optional[int] = 500,
        action: str = '',
        mod: str = '',
    ) -> None:
        cursor_extractor = lambda x: x['data']['id']
        super().__init__(client, uri, limit=limit, cursor_extractor=cursor_extractor)
        self.client = client
        self.uri = uri
        self.action = action
        self.mod = mod

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        if self.action:
            yield ('action', self.action)
        if self.mod:
            yield ('mod', self.mod)

    def next_result(self) -> Sequence[ModerationActionLogEntry]:
        data = self._next_data()
        return [load_mod_log_action_entry(d['data']) for d in data['children']]
