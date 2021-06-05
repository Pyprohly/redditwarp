
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.submission_comment_thread_SYNC import SubmissionCommentThread
    from .SYNC import Thread as Outer

from ...util.base_conversion import to_base36
from ...exceptions import NoResultException

class Fetch:
    def __init__(self, outer: Outer, client: Client):
        self._outer = outer
        self._client = client

    def __call__(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionCommentThread:
        return self.by_id(submission_id, comment_id, sort, limit, depth, context)

    def by_id(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> SubmissionCommentThread:
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
    ) -> SubmissionCommentThread:
        v = self._outer.get.by_id36(
            submission_id36,
            comment_id36,
            sort,
            limit,
            depth,
            context,
        )
        if v is None:
            raise NoResultException('target not found')
        return v
