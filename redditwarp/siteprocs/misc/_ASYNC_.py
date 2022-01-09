
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping, Any
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.submission_ASYNC import Submission

import json

from ...paginators.paginator_chaining_async_iterator import ImpartedPaginatorChainingAsyncIterator
from ...paginators.implementations.submission_async import SearchSubmissionsListingAsyncPaginator

class MiscProcedures:
    def __init__(self, client: Client):
        self._client = client

    def search_submissions(self, query: str, amount: Optional[int] = None, *,
        time_filter: str = 'all', sort: str = 'relevance',
    ) -> ImpartedPaginatorChainingAsyncIterator[SearchSubmissionsListingAsyncPaginator, Submission]:
        p = SearchSubmissionsListingAsyncPaginator(self._client, '/search',
            params={'q': query},
            time_filter=time_filter, sort=sort)
        return ImpartedPaginatorChainingAsyncIterator(p, amount)

    async def convert_rtjson_to_markdown(self, rtjson: Mapping[str, Any]) -> str:
        root = await self._client.request('POST', '/api/convert_rte_body_format',
                data={'output_mode': 'markdown', 'richtext_json': json.dumps(rtjson)})
        return root['output']

    async def convert_markdown_to_rtjson(self, md: str) -> Mapping[str, Any]:
        root = await self._client.request('POST', '/api/convert_rte_body_format',
                data={'output_mode': 'rtjson', 'markdown_text': md})
        return root['output']
