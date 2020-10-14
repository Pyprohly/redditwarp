
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional, Sequence
if TYPE_CHECKING:
    from .more_comments_SYNC import MoreComments

from .comment_SYNC import Comment
from .submission_SYNC import Submission
from ..util.tree_node import GeneralTreeNode, IGeneralTreeNode

E = TypeVar('E')

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


class ICommentRepliesTreeNode(IGeneralTreeNode):
    pass

TCommentRepliesTreeNodeInterface = TypeVar('TCommentRepliesTreeNodeInterface', bound=ICommentRepliesTreeNode)

class CommentRepliesTreeNode(ICommentRepliesTreeNode, GeneralTreeNode[TCommentRepliesTreeNodeInterface, E]):
    def __init__(self,
        value: E,
        children: Sequence[TCommentRepliesTreeNodeInterface],
        more: Optional[MoreComments],
    ):
        super().__init__(value, children)
        self.more = more

__bound = 'CommentRepliesTreeNode[TCommentRepliesTreeNode, E]'
TCommentRepliesTreeNode = TypeVar('TCommentRepliesTreeNode', bound=CommentRepliesTreeNode)  # type: ignore[type-arg]


class CommentTreeNode(CommentRepliesTreeNode['CommentTreeNode', Comment]):
    pass

class SubmissionCommentTreeNode(CommentRepliesTreeNode[CommentTreeNode, Submission]):
    pass
