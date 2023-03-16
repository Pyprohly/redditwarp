
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator, MutableSequence, Callable
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import CommentSubtreeTreeNode, MoreCommentsTreeNode

from collections import deque

from redditwarp.models.comment_SYNC import Comment

#region::literalinclude
def breadth_first_accurate(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
    level = 0
    queue: MutableSequence[bool] = deque([True])
    node_queue: MutableSequence[CommentSubtreeTreeNode[object]] = deque([node])
    more_queue: MutableSequence[Callable[[], MoreCommentsTreeNode]] = deque()
    while queue:
        batch = deque(queue)
        node_batch = deque(node_queue)
        more_batch = deque(more_queue)
        queue.clear()
        node_queue.clear()
        more_queue.clear()
        while batch:
            if batch.popleft():
                node = node_batch.pop()
            else:
                node = more_batch.pop()()

            if node.value is None:
                if node.more:
                    batch.appendleft(False)
                    more_batch.appendleft(node.more)
                batch.extendleft([True] * len(node.children))
                node_batch.extendleft(reversed(node.children))
                continue

            value = node.value
            if isinstance(value, Comment):
                yield (level, value)

            queue.extend([True] * len(node.children))
            node_queue.extend(node.children)
            if node.more:
                queue.append(False)
                more_queue.append(node.more)

        level += 1
#endregion
