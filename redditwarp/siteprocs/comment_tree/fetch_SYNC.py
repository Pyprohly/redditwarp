
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Iterable
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_tree_SYNC import SubmissionTreeNode
    from .SYNC import CommentTreeProcedures

from ...util.base_conversion import to_base36
from ...model_loaders.comment_tree_SYNC import load_submission_tree_node
from ...exceptions import RejectedResultException

class Fetch:
    def __init__(self, outer: CommentTreeProcedures, client: Client):
        self._outer = outer
        self._client = client

    def __call__(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionTreeNode:
        submission_id36 = to_base36(submission_id)
        comment_id36 = None if comment_id is None else to_base36(comment_id)
        return self.by_id36(submission_id36, comment_id36, sort=sort, limit=limit, depth=depth, context=context)

    def by_id36(self,
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

        root = self._client.request('GET', '/comments/' + submission_id36, params=dict(g()))
        tree_node = load_submission_tree_node(root, self._client, sort)

        if comment_id36 is not None and not tree_node.children:
            raise RejectedResultException('''\
The returned comment list is empty so the specified comment was not returned. \
This happens when the comment existed at one point but is no longer available anymore.''')

        return tree_node
