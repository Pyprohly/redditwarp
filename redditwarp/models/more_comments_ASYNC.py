
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from ..exceptions import ResultRejectedException
from .comment_tree_ASYNC import MoreCommentsTreeNode, SubmissionTreeNode
from .more_comments_base import BaseMoreComments

class MoreComments(BaseMoreComments):
    def __init__(self,
        submission_id36: str,
        comment_id36: str,
        sort: str,
        *,
        d: Mapping[str, Any],
        client: Client,
    ):
        super().__init__(submission_id36, comment_id36, sort, d=d)
        self.client: Client = client

    async def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        raise NotImplementedError

class ContinueThisThread(MoreComments):
    async def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        node = await self.fetch_submission_tree_node()

        is_continued = not node.children[0].value.is_top_level
        if not is_continued:
            raise ResultRejectedException(self)

        return MoreCommentsTreeNode(None, node.children[0].children, node.more)

    async def fetch_submission_tree_node(self) -> SubmissionTreeNode:
        return await self.client.p.comment_tree.fetch.by_id36(self.submission_id36, self.comment_id36)

class LoadMoreComments(MoreComments):
    def __init__(self,
        submission_id36: str,
        comment_id36: str,
        sort: str,
        children_id36: Sequence[str],
        count: int,
        *,
        d: Mapping[str, Any],
        client: Client,
    ):
        super().__init__(submission_id36, comment_id36, sort, d=d, client=client)
        self.children_id36: Sequence[str] = children_id36
        self.count: int = count

    async def __call__(self, *,
        depth: Optional[int] = None,
        limit_children: bool = False,
    ) -> MoreCommentsTreeNode:
        return await self.client.p.comment_tree.more_children(
            self.submission_id36,
            self.children_id36,
            sort=self.sort,
            depth=depth,
            limit_children=limit_children,
        )
