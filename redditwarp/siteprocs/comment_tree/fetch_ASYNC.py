
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_tree_ASYNC import SubmissionTreeNode
    from .ASYNC import CommentTreeProcedures

from ...util.base_conversion import to_base36
from ...models.load.comment_tree_ASYNC import load_submission_tree_node

class Fetch:
    def __init__(self, outer: CommentTreeProcedures, client: Client):
        self._outer = outer
        self._client = client

    async def __call__(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
        submission_id36 = to_base36(submission_id)
        comment_id36 = comment_id if comment_id is None else to_base36(comment_id)
        return await self.by_id36(submission_id36, comment_id36, sort=sort, limit=limit, depth=depth, context=context)

    async def by_id36(self,
        submission_id36: str,
        comment_id36: Optional[str] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
        def g() -> Iterable[tuple[str, str]]:
            if comment_id36 is not None:
                yield ('comment', comment_id36)
            if sort:
                yield ('sort', sort)
            if limit is not None:
                yield ('limit', str(limit))
            if depth is not None:
                yield ('depth', str(depth))
            if context is not None:
                yield ('context', str(context))

        root = await self._client.request('GET', '/comments/' + submission_id36, params=dict(g()))
        return load_submission_tree_node(root, self._client, sort)
