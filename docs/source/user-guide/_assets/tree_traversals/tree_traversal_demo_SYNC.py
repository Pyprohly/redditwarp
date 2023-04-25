#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
if TYPE_CHECKING:
    # from typing import MutableSequence, Callable
    from redditwarp.models.comment_tree_SYNC import CommentSubtreeTreeNode
    # from redditwarp.models.comment_tree_SYNC import MoreCommentsTreeNode

# from collections import deque

import redditwarp.SYNC
from redditwarp.models.comment_SYNC import Comment

def traversal(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
    def traverse(root: CommentSubtreeTreeNode[object], level: int = 0) -> Iterator[tuple[int, Comment]]:
        value = root.value
        if isinstance(value, Comment):
            yield (level, value)

        for child in root.children:
            yield from traverse(child, level + 1)

        if root.more:
            yield from traverse(root.more(), level)

    return traverse(node)

client = redditwarp.SYNC.Client()

tree_node = client.p.comment_tree.fetch(1537771841)
for depth, c in traversal(tree_node):
    print(f"{depth*'.'} u/{c.author_display_name} | {c.body!r}"[:80])
