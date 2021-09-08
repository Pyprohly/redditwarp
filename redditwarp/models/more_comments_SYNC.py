
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ..exceptions import ResultRejectedException
from .comment_tree_SYNC import MoreCommentsTreeNode
from .submission_comment_tree_wrapper_SYNC import SubmissionCommentTreeWrapper
from .more_comments_base import BaseMoreComments

class MoreComments(BaseMoreComments):
    def __init__(self,
        submission_id36: str,
        comment_id36: str,
        sort: Optional[str],
        *,
        d: Mapping[str, Any],
        client: Client,
    ):
        super().__init__(submission_id36, comment_id36, sort, d=d)
        self.client = client

    def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        raise NotImplementedError

class ContinueThisThread(MoreComments):
    def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode:
        tree = self.fetch_continued()
        o = tree.node
        return MoreCommentsTreeNode(None, o.children[0].children, o.more)

    def get(self) -> Optional[SubmissionCommentTreeWrapper]:
        return self.client.p.comment_tree.get.by_id36(self.submission_id36, self.comment_id36)

    def fetch(self) -> SubmissionCommentTreeWrapper:
        return self.client.p.comment_tree.fetch.by_id36(self.submission_id36, self.comment_id36)

    def fetch_continued(self) -> SubmissionCommentTreeWrapper:
        tree = self.fetch()
        if not tree.is_continued():
            raise ResultRejectedException(self)
        return tree

class LoadMoreComments(MoreComments):
    def __init__(self,
        submission_id36: str,
        comment_id36: str,
        sort: Optional[str],
        children_id36: Sequence[str],
        count: int,
        *,
        d: Mapping[str, Any],
        client: Client,
    ):
        super().__init__(submission_id36, comment_id36, sort, d=d, client=client)
        self.children_id36 = children_id36
        self.count = count

    def __call__(self, *,
        depth: Optional[int] = None,
        limit_children: bool = False,
    ) -> MoreCommentsTreeNode:
        return self.client.p.comment_tree.more_children(
            self.submission_id36,
            self.children_id36,
            sort=self.sort,
            depth=depth,
            limit_children=limit_children,
        )
