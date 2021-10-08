
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_SYNC import Client

from .listing_paginator import ListingPaginator
from ....models.mod_log_action_entry import ModLogActionEntry
from ....models.load.mod_log_action_entry import load_mod_log_action_entry

class ModerationActionsPaginator(ListingPaginator[ModLogActionEntry]):
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

    def next_result(self) -> Sequence[ModLogActionEntry]:
        data = self._next_data()
        return [load_mod_log_action_entry(d['data']) for d in data['children']]
