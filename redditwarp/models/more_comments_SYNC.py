
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Any
if TYPE_CHECKING:
    from .comment_tree_SYNC import CommentTreeNode
    from ..client_SYNC import Client

from .comment_tree_SYNC import MoreCommentsTreeNode
from .more_comments_base import MoreCommentsBase
from .subreddit_thread_SYNC import SubredditThread
from ..exceptions import UnexpectedServiceRequestResultError, ClientRejectedResultException

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
    ) -> MoreCommentsTreeNode[None, CommentTreeNode]:
        raise NotImplementedError

class ContinueThisThread(MoreComments):
    def __call__(self, *,
        depth: Optional[int] = None,
    ) -> MoreCommentsTreeNode[None, CommentTreeNode]:
        thread = self.fetch_continued_thread()
        return MoreCommentsTreeNode(None, thread.comments[0].children, thread.more)

    def get_thread(self) -> Optional[SubredditThread]:
        return self.client.api.thread.get.by_id36(self.submission_id36, self.comment_id36)

    def fetch_continued_thread(self) -> SubredditThread:
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
        children: Sequence[str],
        count: int,
        *,
        d: Mapping[str, Any],
        client: Client,
    ):
        super().__init__(submission_id36, comment_id36, sort, d=d, client=client)
        self.children = children
        self.count = count

    def __call__(self, *,
        depth: Optional[int] = None,
        limit_children: bool = False,
    ) -> MoreCommentsTreeNode[None, CommentTreeNode]:
        return self.client.api.thread.more_children(
            self.submission_id36,
            self.children,
            sort=self.sort,
            depth=depth,
            limit_children=limit_children,
        )
