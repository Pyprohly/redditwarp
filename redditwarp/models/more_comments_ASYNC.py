
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..client_ASYNC import Client

from functools import cached_property

from .comment_tree_ASYNC import MoreCommentsTreeNode

class MoreComments:
    @cached_property
    def submission_id(self) -> int:
        return int(self.submission_id36, 36)

    @cached_property
    def comment_id(self) -> int:
        return int(self.comment_id36, 36)

    def __init__(self,
        *,
        submission_id36: str,
        comment_id36: str,
        sort: str,
        d: Mapping[str, Any],
        client: Client,
    ):
        self.submission_id36: str = submission_id36
        self.comment_id36: str = comment_id36
        self.sort: str = sort
        self.d: Mapping[str, Any] = d
        self.client: Client = client

    async def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        raise NotImplementedError

class ContinueThisThread(MoreComments):
    async def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        node = await self.client.p.comment_tree.fetch.by_id36(self.submission_id36, self.comment_id36)

        first_child = node.children[0]
        if first_child.value.id36 != self.comment_id36:
            raise Exception('assertion: 1')
        if len(node.children) != 1:
            raise Exception('assertion: 2')

        return MoreCommentsTreeNode(None, first_child.children, node.more)

class LoadMoreComments(MoreComments):
    def __init__(self,
        *,
        submission_id36: str,
        comment_id36: str,
        child_id36s: Sequence[str],
        sort: str,
        count: int,
        d: Mapping[str, Any],
        client: Client,
    ):
        super().__init__(
            submission_id36=submission_id36,
            comment_id36=comment_id36,
            sort=sort,
            d=d,
            client=client,
        )
        self.child_id36s: Sequence[str] = child_id36s
        self.count: int = count

    async def __call__(self, *,
        depth: Optional[int] = None,
        exact: bool = False,
    ) -> MoreCommentsTreeNode:
        return await self.client.p.comment_tree.more_children.by_id36(
            self.submission_id36,
            self.child_id36s,
            sort=self.sort,
            depth=depth,
            exact=exact,
        )
