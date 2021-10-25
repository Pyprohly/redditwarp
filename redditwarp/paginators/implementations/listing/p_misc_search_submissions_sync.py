
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Mapping, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client

from ....models.submission_SYNC import Submission
from .mixins.time_filter_SYNC import TimeFilter
from .mixins.sort_SYNC import Sort
from .submission_listing_paginator_sync import SubmissionListingPaginator

class SearchSubmissionsListingPaginator(
    TimeFilter[Submission],
    Sort[Submission],
    SubmissionListingPaginator,
):
    def __init__(self,
        client: Client,
        uri: str,
        *,
        params: Optional[Mapping[str, str]] = None,
        time_filter: str = 'all',
        sort: str = 'relevance',
    ):
        super().__init__(client, uri, params=params)
        self.time_filter: str = time_filter
        self.sort: str = sort

    def _generate_params(self) -> Iterable[tuple[str, str]]:
        yield from super()._generate_params()
