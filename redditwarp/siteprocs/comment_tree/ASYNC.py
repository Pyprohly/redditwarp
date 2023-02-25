
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from ...client_ASYNC import Client
    from ...models.comment_tree_ASYNC import MoreCommentsTreeNode, SubmissionTreeNode

from ...util.base_conversion import to_base36
from .low_ASYNC import Low

class CommentTreeProcedures:
    def __init__(self, client: Client) -> None:
        self._client = client
        self.low: Low = Low(self, client)

    async def get(self,
        submission_id: int,
        comment_id: Optional[int] = None,
        *,
        sort: str = 'confidence',
        limit: Optional[int] = None,
        depth: Optional[int] = None,
        context: Optional[int] = None,
    ) -> Optional[SubmissionTreeNode]:
        submission_id36 = to_base36(submission_id)
        comment_id36 = None if comment_id is None else to_base36(comment_id)
        return await self.low.get(
            submission_id36,
            comment_id36,
            sort=sort,
            limit=limit,
            depth=depth,
            context=context,
        )

    async def fetch(self,
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
        return await self.low.fetch(
            submission_id36,
            comment_id36,
            sort=sort,
            limit=limit,
            depth=depth,
            context=context,
        )

    async def fetch_lenient(self,
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
        return await self.low.fetch(
            submission_id36,
            comment_id36,
            sort=sort,
            limit=limit,
            depth=depth,
            context=context,
        )

    async def more_children(self,
        submission_id: int,
        child_ids: Iterable[int],
        *,
        sort: str = '',
        depth: Optional[int] = None,
        exact: bool = False,
    ) -> MoreCommentsTreeNode:
        submission_id36 = to_base36(submission_id)
        child_id36s = (to_base36(x) for x in child_ids)
        return await self.low.more_children(
            submission_id36,
            child_id36s,
            sort=sort,
            depth=depth,
            exact=exact,
        )
