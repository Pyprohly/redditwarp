
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Sequence, Mapping, Any
if TYPE_CHECKING:
    from ...client_SYNC import Client

import json

#from ...paginators.implementations.listing.subreddit_listing_paginator_sync import SubredditListingPaginator
#from ...paginators.implementations.listing.submission_listing_paginator_sync import SubmissionListingPaginator

class Misc:
    def __init__(self, client: Client):
        self._client = client

    '''
    def search_reddit(self,
        query: str,
    ) -> tuple[
        tuple[Sequence[Subreddit], SubredditListingPaginator],
        tuple[Sequence[Submission], SubmissionListingPaginator],
    ]:
        root = self._client.request('GET', '/search', params={'type': 'sr,link', 'q': query})

    def search_reddit_subreddits(self, query: str) -> SubredditListingPaginator:
        return SubredditListingPaginator(self._client, '/search', params={'type': 'sr', 'q': query})

    def search_reddit_submissions(self,
        query: str,
        *,
        subreddit: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> SubmissionListingPaginator:
        return SubmissionListingPaginator(self._client, '/search', params={'type': 'link', 'q': query})
    '''

    def convert_rtjson_to_markdown(self, rtjson: Mapping[str, Any]) -> str:
        root = self._client.request('POST', '/api/convert_rte_body_format',
                data={'output_mode': 'markdown', 'richtext_json': json.dumps(rtjson)})
        return root['output']

    def convert_markdown_to_rtjson(self, md: str) -> Mapping[str, Any]:
        root = self._client.request('POST', '/api/convert_rte_body_format',
                data={'output_mode': 'rtjson', 'markdown_text': md})
        return root['output']
