
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import CommentSubtreeTreeNode

from redditwarp.models.comment_SYNC import Comment

#region::literalinclude
def depth_first_recursive(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
    def traverse(root: CommentSubtreeTreeNode[object], level: int = 0) -> Iterator[tuple[int, Comment]]:
        value = root.value
        if isinstance(value, Comment):
            yield (level, value)

        for child in root.children:
            yield from traverse(child, level + 1)

        if root.more:
            yield from traverse(root.more(), level)

    return traverse(node)
#endregion
