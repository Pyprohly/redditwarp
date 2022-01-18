
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Iterable
if TYPE_CHECKING:
    from ....client_ASYNC import Client

from ...listing.listing_async_paginator import ListingAsyncPaginator
from ....models.moderation_action_log_entry import ModerationActionLogEntry
from ....models.load.moderation_action_log_entry import load_mod_log_action_entry

class ModerationActionLogAsyncPaginator(ListingAsyncPaginator[ModerationActionLogEntry]):
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
        self.client: Client = client
        self.uri: str = uri
        self.action: str = action
        self.mod: str = mod

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
        if self.action:
            yield ('action', self.action)
        if self.mod:
            yield ('mod', self.mod)

    async def fetch(self) -> Sequence[ModerationActionLogEntry]:
        data = await self._fetch_data()
        return [load_mod_log_action_entry(d['data']) for d in data['children']]
