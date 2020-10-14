
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence
if TYPE_CHECKING:
    from .more_comments_SYNC import MoreComments

from .comment_SYNC import Comment
from .submission_SYNC import Submission
from ..util.tree_node import GeneralTreeNode

T = TypeVar('T')
TChild = TypeVar('TChild')

class CommentRepliesTreeNode(GeneralTreeNode[T, TChild]):
    def __init__(self,
        value: T,
        children: Sequence[TChild],
        more: Optional[MoreComments],
    ):
        super().__init__(value, children)
        self.more = more

__bound = 'CommentRepliesTreeNode[T, TCommentRepliesTreeNode]'
TCommentRepliesTreeNode = TypeVar('TCommentRepliesTreeNode', bound=CommentRepliesTreeNode)  # type: ignore[type-arg]


class CommentTreeNode(CommentRepliesTreeNode[Comment, 'CommentTreeNode']):
    pass

class SubmissionCommentTreeNode(CommentRepliesTreeNode[Submission, CommentTreeNode]):
    pass
