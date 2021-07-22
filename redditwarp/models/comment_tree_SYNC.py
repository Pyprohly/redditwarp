
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence
if TYPE_CHECKING:
    from .more_comments_SYNC import MoreComments

from ..util.tree_node import GeneralTreeNode
from .comment_SYNC import NormalComment
from .submission_SYNC import Submission

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
        self.more = more

class MoreCommentsTreeNode(CommentSubtreeTreeNode[None]):
    pass

class CommentTreeNode(CommentSubtreeTreeNode[NormalComment]):
    pass

class SubmissionTreeNode(CommentSubtreeTreeNode[Submission]):
    pass
