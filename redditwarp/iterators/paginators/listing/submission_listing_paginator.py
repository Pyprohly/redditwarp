
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Dict, Any
if TYPE_CHECKING:
    from ....client_sync import Client

from .listing_paginator import ListingPaginator
from ....api.load.submission import load_submission
from ....models.submission import Submission

class SubmissionListingPaginator(ListingPaginator[Sequence[Submission]]):
    def __init__(self, client: Client, uri: str) -> None:
        super().__init__()
        self._client = client
        self._uri = uri

    def __next__(self) -> Sequence[Submission]:
        params: Dict[str, Any] = {
            'count': self.count,
            'limit': self.limit,
        }
        if self.show_all:
            params['show'] = 'all'
        if self.include_subreddit_data:
            params['sr_detail'] = '1'

        if self.forward:
            params['after'] = self.cursor
        else:
            params['before'] = self.back_cursor

        recv = self._client.request('GET', self._uri, params=params)
        data = recv['data']

        self.cursor = data['after']
        self.back_cursor = data['before']
        self.count += data['dist']

        self.has_next = bool(self.cursor)
        self.has_prev = bool(self.back_cursor)

        return [load_submission(d) for d in data['children']]
