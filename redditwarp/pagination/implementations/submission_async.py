
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Mapping, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client

from ...models.submission_ASYNC import Submission
from ..listing.mixins.time_filter_ASYNC import TimeFilter
from ..listing.mixins.sort_ASYNC import Sort
from ..listing.submission_listing_async_paginator import SubmissionListingAsyncPaginator

class SearchSubmissionsListingAsyncPaginator(
    TimeFilter[Submission],
    Sort[Submission],
    SubmissionListingAsyncPaginator,
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
