
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional
if TYPE_CHECKING:
    from .more_comments_ASYNC import MoreComments

from dataclasses import dataclass

from ..util.tree_node import TreeNode
from .comment_ASYNC import Comment
from .submission_ASYNC import Submission

TValue_co = TypeVar('TValue_co', covariant=True)

@dataclass(repr=False, eq=False, frozen=True)
class CommentSubtreeTreeNode(TreeNode[TValue_co, 'CommentTreeNode']):
    more: Optional[MoreComments]

class MoreCommentsTreeNode(CommentSubtreeTreeNode[None]):
    pass

class CommentTreeNode(CommentSubtreeTreeNode[Comment]):
    pass

class SubmissionTreeNode(CommentSubtreeTreeNode[Submission]):
    pass
