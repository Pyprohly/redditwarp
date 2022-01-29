
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_tree_SYNC import MoreCommentsTreeNode

from ...models.load.comment_tree_SYNC import load_more_children
from .get_SYNC import Get
from .fetch_SYNC import Fetch

class CommentTreeProcedures:
    def __init__(self, client: Client):
        self._client = client
        self.get: Get = Get(self, client)
        self.fetch: Fetch = Fetch(self, client)

    def more_children(self,
        submission_id36: str,
        children_id36: Iterable[str],
        *,
        sort: str = '',
        depth: Optional[int] = None,
        limit_children: bool = False,
    ) -> MoreCommentsTreeNode:
        def g() -> Iterable[tuple[str, str]]:
            yield ('link_id', 't3_' + submission_id36)
            yield ('children', ','.join(children_id36))
            if sort:
                yield ('sort', sort)
            if depth is not None:
                yield ('depth', str(depth))
            if limit_children:
                yield ('limit_children', '1')

        resp_data = self._client.request('GET', '/api/morechildren', params=dict(g()))
        return load_more_children(resp_data, self._client, submission_id36, sort)
