
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...models.submission_comment_tree_wrapper_SYNC import SubmissionCommentTreeWrapper
    from .SYNC import CommentTree as Outer

from ...util.base_conversion import to_base36
from ...exceptions import HTTPStatusError

class Get:
    def __init__(self, outer: Outer):
        self._outer = outer
        self._client = outer._client

    def __call__(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        sort: Optional[str] = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubmissionCommentTreeWrapper]:
        return self.by_id(submission_id, comment_id, sort, limit, depth, context)

    def by_id(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        sort: Optional[str] = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubmissionCommentTreeWrapper]:
        submission_id36 = to_base36(submission_id)
        comment_id36 = comment_id if comment_id is None else to_base36(comment_id)
        return self.by_id36(submission_id36, comment_id36, sort, limit, depth, context)

    def by_id36(self,
        submission_id36: str,
        comment_id36: Optional[str] = None,
        sort: Optional[str] = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubmissionCommentTreeWrapper]:
        try:
            v = self._outer.fetch.by_id36(
                submission_id36,
                comment_id36,
                sort,
                limit,
                depth,
                context,
            )
        except HTTPStatusError as e:
            if e.response.status == 404:
                return None
            raise
        return v
