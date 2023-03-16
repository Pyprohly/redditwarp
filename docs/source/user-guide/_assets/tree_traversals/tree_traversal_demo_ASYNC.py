#!/usr/bin/env python
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncIterator
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_ASYNC import CommentSubtreeTreeNode

import asyncio

import redditwarp.ASYNC
from redditwarp.models.comment_ASYNC import Comment

def traversal(node: CommentSubtreeTreeNode[object]) -> AsyncIterator[tuple[int, Comment]]:
    async def traverse(root: CommentSubtreeTreeNode[object], level: int = 0) -> AsyncIterator[tuple[int, Comment]]:
        value = root.value
        if isinstance(value, Comment):
            yield (level, value)

        for child in root.children:
            async for i in traverse(child, level + 1):
                yield i

        if root.more:
            async for i in traverse(await root.more(), level):
                yield i

    return traverse(node)

async def main() -> None:
    client = redditwarp.ASYNC.Client()
    tree_node = await client.p.comment_tree.fetch(1537771841)
    async for depth, comment in traversal(tree_node):
        print(depth, comment.author_display_name, repr(comment.body)[:10])

asyncio.run(main())
