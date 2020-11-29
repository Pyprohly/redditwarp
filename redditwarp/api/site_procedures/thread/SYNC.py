
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional
if TYPE_CHECKING:
    from ....client_SYNC import Client
    from ....models.comment_tree_SYNC import MoreCommentsTreeNode, CommentTreeNode

from .get_SYNC import Get
from ...load.comment_tree_SYNC import load_more_children

class Thread:
    def __init__(self, client: Client):
        self._client = client
        self.get = Get(client)

    def more_children(self,
        submission_id36: str,
        children: Sequence[str],
        sort: Optional[str] = None,
        depth: Optional[int] = None,
        limit_children: bool = False,
    ) -> MoreCommentsTreeNode[None, CommentTreeNode]:
        params = {
            'link_id': 't3_' + submission_id36,
            'children': ','.join(children),
        }
        if sort is not None:
            params['sort'] = sort
        if depth is not None:
            params['depth'] = str(depth)
        if limit_children:
            params['limit_children'] = '1'

        resp_data = self._client.request('GET', '/api/morechildren', params=params)
        return load_more_children(resp_data, self._client, submission_id36, sort)
