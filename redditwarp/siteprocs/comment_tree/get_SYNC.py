
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.comment_tree_SYNC import SubmissionTreeNode
    from .SYNC import CommentTreeProcedures

from ...util.base_conversion import to_base36
from ... import http

class Get:
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
    ) -> Optional[SubmissionTreeNode]:
        submission_id36 = to_base36(submission_id)
        comment_id36 = comment_id if comment_id is None else to_base36(comment_id)
        return self.by_id36(submission_id36, comment_id36, sort=sort, limit=limit, depth=depth, context=context)

    def by_id36(self,
        submission_id36: str,
        comment_id36: Optional[str] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubmissionTreeNode]:
        try:
            v = self._outer.fetch.by_id36(
                submission_id36,
                comment_id36,
                sort=sort,
                limit=limit,
                depth=depth,
                context=context,
            )
        except http.exceptions.StatusCodeException as e:
            if e.status_code == 404:
                return None
            raise
        return v
