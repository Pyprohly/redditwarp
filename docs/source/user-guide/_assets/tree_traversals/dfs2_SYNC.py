
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, MutableSequence, Callable
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import CommentSubtreeTreeNode, MoreCommentsTreeNode

from collections import deque

from redditwarp.models.comment_SYNC import Comment

#region::literalinclude
def depth_first_iterative_accurate(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
    stack: MutableSequence[bool] = deque([True])
    node_stack: MutableSequence[CommentSubtreeTreeNode[object]] = deque([node])
    more_stack: MutableSequence[Callable[[], MoreCommentsTreeNode]] = deque()
    levels = deque([0])
    while stack:
        if stack.pop():
            node = node_stack.pop()
        else:
            node = more_stack.pop()()
        level = levels.pop()

        value = node.value
        if isinstance(value, Comment):
            yield (level, value)

        if node.more:
            stack.append(False)
            more_stack.append(node.more)
            levels.append(level)

        stack.extend([True] * len(node.children))
        node_stack.extend(reversed(node.children))
        levels.extend([level + 1] * len(node.children))
#endregion
