
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional, Mapping, Any
if TYPE_CHECKING:
    from .comment_tree_SYNC import CommentTreeNode
    from ..client_SYNC import Client

from .more_comments_base import MoreCommentsBase
from .comment_tree_SYNC import TopicThread
from ..exceptions import UnexpectedRequestResultError, ClientRefusedResultException

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
    ) -> Sequence[CommentTreeNode]:
        raise NotImplementedError

class ContinueThisThread(MoreComments):
    def __call__(self, *,
        depth: Optional[int] = None,
    ) -> Sequence[CommentTreeNode]:
        thread = self.fetch_continued_thread()
        if thread is None:
            raise UnexpectedRequestResultError(self)
        return thread.comments[0].children

    def fetch_continued_thread(self) -> Optional[TopicThread]:
        thread = self.client.api.thread.fetch.by_id36(self.submission_id36, self.comment_id36)
        if thread is None:
            return None
        if thread.comments[0].value.parent_comment_id is None:
            raise ClientRefusedResultException(self)
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
        super().__init__(submission_id36, comment_id36, sort,
                d=d, client=client)
        self.children = children
        self.count = count

    def __call__(self, *,
        depth: Optional[int] = None,
        limit_children: bool = False,
    ) -> Sequence[CommentTreeNode]:
        link_id = 't3_' + self.submission_id36
        nodes = self.client.api.thread.more_children(
            link_id,
            self.children,
            sort=self.sort,
            depth=depth,
            limit_children=limit_children,
        )
        if nodes is None:
            return []
        return nodes
