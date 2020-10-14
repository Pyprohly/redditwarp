
from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Optional
if TYPE_CHECKING:
    from .comment_tree_SYNC import CommentTreeNode, SubmissionCommentTreeNode
    from .submission_SYNC import Submission
    from .more_comments_SYNC import MoreComments

class TopicThread:
    @property
    def submission(self) -> Submission:
        return self.node.value

    @property
    def comments(self) -> Sequence[CommentTreeNode]:
        return self.node.children

    @property
    def more(self) -> Optional[MoreComments]:
        return self.node.more

    def __init__(self, node: SubmissionCommentTreeNode, sort: Optional[str]):
        self.node = node
        self.sort = sort

    def is_continued(self) -> bool:
        try:
            return not self.comments[0].value.is_top_level
        except IndexError:
            return False
