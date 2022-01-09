
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence
if TYPE_CHECKING:
    from .more_comments_ASYNC import MoreComments

from ..util.tree_node import GeneralTreeNode
from .comment_ASYNC import Comment
from .submission_ASYNC import Submission

T = TypeVar('T')

class ICommentSubtreeTreeNode:
    pass

class CommentSubtreeTreeNode(ICommentSubtreeTreeNode, GeneralTreeNode[T, 'CommentTreeNode']):
    def __init__(self,
        value: T,
        children: Sequence[CommentTreeNode],
        more: Optional[MoreComments],
    ):
        super().__init__(value, children)
        self.more: Optional[MoreComments] = more

class MoreCommentsTreeNode(CommentSubtreeTreeNode[None]):
    pass

class CommentTreeNode(CommentSubtreeTreeNode[Comment]):
    pass

class SubmissionTreeNode(CommentSubtreeTreeNode[Submission]):
    pass
