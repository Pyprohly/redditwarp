
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, MutableSequence
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import CommentSubtreeTreeNode

from collections import deque

from redditwarp.models.comment_SYNC import Comment

#region::literalinclude
def depth_first_iterative_inaccurate(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
    stack: MutableSequence[CommentSubtreeTreeNode[object]] = deque([node])
    levels = deque([0])
    while stack:
        node = stack.pop()
        level = levels.pop()

        value = node.value
        if isinstance(value, Comment):
            yield (level, value)

        if node.more:
            stack.append(node.more())
            levels.append(level)

        stack.extend(reversed(node.children))
        levels.extend([level + 1] * len(node.children))
#endregion
