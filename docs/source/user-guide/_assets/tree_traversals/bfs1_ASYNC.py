
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncIterator, MutableSequence
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_ASYNC import CommentSubtreeTreeNode

from collections import deque

from redditwarp.models.comment_ASYNC import Comment

#region::literalinclude
async def breadth_first_inaccurate(node: CommentSubtreeTreeNode[object]) -> AsyncIterator[tuple[int, Comment]]:
    level = 0
    queue: MutableSequence[CommentSubtreeTreeNode[object]] = deque([node])
    while queue:
        batch = deque(queue)
        queue.clear()
        while batch:
            node = batch.popleft()
            if node.value is None:
                if node.more:
                    batch.appendleft(await node.more())
                batch.extendleft(reversed(node.children))
                continue

            value = node.value
            if isinstance(value, Comment):
                yield (level, value)

            queue.extend(node.children)
            if node.more:
                queue.append(await node.more())

        level += 1
#endregion
