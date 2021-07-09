
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Any
if TYPE_CHECKING:
    from ..client_SYNC import Client

from ..exceptions import UnexpectedServiceRequestResultError, ClientRejectedResultException
from .comment_tree_SYNC import MoreCommentsTreeNode
from .more_comments_base import MoreCommentsBase
from .submission_comment_thread_SYNC import SubmissionCommentThread

class MoreComments(MoreCommentsBase):
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
        thread = self.fetch_continued_thread()
        o = thread.node
        return MoreCommentsTreeNode(None, o.children[0].children, o.more)

    def get_thread(self) -> Optional[SubmissionCommentThread]:
        return self.client.p.thread.get.by_id36(self.submission_id36, self.comment_id36)

    def fetch_continued_thread(self) -> SubmissionCommentThread:
        thread = self.get_thread()
        if thread is None:
            raise UnexpectedServiceRequestResultError(self)
        if not thread.is_continued():
            raise ClientRejectedResultException(self)
        return thread

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
        return self.client.p.thread.more_children(
            self.submission_id36,
            self.children_id36,
            sort=self.sort,
            depth=depth,
            limit_children=limit_children,
        )
