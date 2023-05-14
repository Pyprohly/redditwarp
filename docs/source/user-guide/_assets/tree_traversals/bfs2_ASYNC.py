
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncIterator, MutableSequence, Callable, Awaitable
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_ASYNC import CommentSubtreeTreeNode, MoreCommentsTreeNode

from collections import deque

from redditwarp.models.comment_ASYNC import Comment

#region::literalinclude
async def breadth_first_accurate(node: CommentSubtreeTreeNode[object]) -> AsyncIterator[tuple[int, Comment]]:
    level = 0
    queue: MutableSequence[bool] = deque([True])
    node_queue: MutableSequence[CommentSubtreeTreeNode[object]] = deque([node])
    more_queue: MutableSequence[Callable[[], Awaitable[MoreCommentsTreeNode]]] = deque()
    while queue:
        batch = deque(queue)
        node_batch = deque(node_queue)
        more_batch = deque(more_queue)
        queue.clear()
        node_queue.clear()
        more_queue.clear()
        while batch:
            if batch.popleft():
                node = node_batch.popleft()
            else:
                node = await more_batch.popleft()()

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
