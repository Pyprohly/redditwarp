
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.comment_tree_SYNC import CommentTreeNode

from .fetch_SYNC import Fetch
from ...load.comment_tree_SYNC import load_more_children
from ....exceptions import HTTPStatusError

class Thread:
    def __init__(self, client: Client):
        self._client = client
        self.fetch = Fetch(client)

    def more_children(self,
        link_id: str,
        children: Sequence[str],
        sort: Optional[str] = None,
        depth: Optional[int] = None,
        limit_children: bool = False,
    ) -> Optional[Sequence[CommentTreeNode]]:
        params = {
            'link_id': link_id,
            'children': ','.join(children),
        }
        if sort is not None:
            params['sort'] = sort
        if depth is not None:
            params['depth'] = str(depth)
        if limit_children:
            params['limit_children'] = '1'

        try:
            resp_data = self._client.request('GET', '/api/morechildren', params=params)
        except HTTPStatusError as e:
            if e.response.status == 403:
                return None
            raise

        return load_more_children(resp_data, self._client, link_id, sort)
