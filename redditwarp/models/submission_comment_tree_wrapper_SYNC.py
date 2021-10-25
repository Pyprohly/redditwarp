
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .comment_tree_SYNC import SubmissionTreeNode

class SubmissionCommentTreeWrapper:
    def __init__(self, node: SubmissionTreeNode, sort: Optional[str]):
        self.node: SubmissionTreeNode = node
        self.sort: Optional[str] = sort

    def is_continued(self) -> bool:
        if children := self.node.children:
            return not children[0].value.is_top_level
        return False
