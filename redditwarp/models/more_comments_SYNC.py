
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from functools import cached_property

from .comment_tree_SYNC import MoreCommentsTreeNode

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

    def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        raise NotImplementedError

class ContinueThisThread(MoreComments):
    def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        node = self.client.p.comment_tree.fetch.by_id36(self.submission_id36, self.comment_id36)
        return MoreCommentsTreeNode(None, node.children[0].children, node.more)

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

    def __call__(self, *,
        depth: Optional[int] = None,
        exact: bool = False,
    ) -> MoreCommentsTreeNode:
        return self.client.p.comment_tree.more_children.by_id36(
            self.submission_id36,
            self.child_id36s,
            sort=self.sort,
            depth=depth,
            exact=exact,
        )
