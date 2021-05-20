
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.subreddit_thread_SYNC import SubredditThread

from ...util.base_conversion import to_base36
from ...models.load.comment_tree_SYNC import load_subreddit_thread
from ...exceptions import HTTPStatusError

class Get:
    def __init__(self, client: Client):
        self._client = client

    def __call__(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubredditThread]:
        return self.by_id(submission_id, comment_id, sort, limit, depth, context)

    def by_id(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubredditThread]:
        submission_id36 = to_base36(submission_id)
        comment_id36 = comment_id if comment_id is None else to_base36(comment_id)
        return self.by_id36(submission_id36, comment_id36, sort, limit, depth, context)

    def by_id36(self,
        submission_id36: str,
        comment_id36: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubredditThread]:
        d = {
            'sort': sort,
            'limit': limit,
            'depth': depth,
            'context': context,
        }
        if comment_id36 is not None:
            d['comment'] = comment_id36
        params = {k: str(v) for k, v in d.items() if v is not None}

        try:
            resp_data = self._client.request(
                'GET',
                '/comments/' + submission_id36,
                params=params,
            )
        except HTTPStatusError as e:
            if e.response.status == 404:
                return None
            raise

        return load_subreddit_thread(resp_data, self._client, sort)
