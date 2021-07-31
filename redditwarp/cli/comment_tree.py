
from __future__ import annotations
from typing import TYPE_CHECKING, MutableSequence, cast, Iterator
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import ICommentSubtreeTreeNode, CommentSubtreeTreeNode, T

import sys
import shutil
from collections import deque

import redditwarp
from redditwarp.models.comment_SYNC import Comment

ALGO_CHOICES = {
    'iterative-depth-first-search': 'dfs',
    'depth-first-search': 'dfs',
    'dfs': 'dfs',
    'recursive-depth-first-search': 'recursive-depth-first-search',
    'iterative-breadth-first-search': 'bfs',
    'breadth-first-search': 'bfs',
    'bfs': 'bfs',
}
COMMENT_SORT_CHOICES = 'confidence top new controversial old random qa live'.split()

import argparse
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
parser._optionals.title = __import__('gettext').gettext('named arguments')
add = parser.add_argument
add('submission_id')
add('--access-token', required=True)
add('-a', '--algo', '--algorithm', choices=ALGO_CHOICES, default='dfs', dest='algo', metavar='')
add('--comment-sort', '--sort', dest='comment_sort', choices=COMMENT_SORT_CHOICES)
args = parser.parse_args()

subm_idt: str = args.submission_id
access_token: str = args.access_token
chosen_algo: str = args.algo
comment_sort: str = args.comment_sort

algo = ALGO_CHOICES[chosen_algo]
if algo == 'recursive-depth-first-search':
    def traversal(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
        def dfs(
            root: CommentSubtreeTreeNode[T],
            level: int = 0,
        ) -> Iterator[tuple[int, Comment]]:
            value = root.value

            if isinstance(value, Comment):
                yield (level, value)

            for child in root.children:
                dfs(child, level + 1)

            if root.more:
                dfs(root.more(), level)

        return dfs(cast("CommentSubtreeTreeNode[object]", node))

elif algo == 'dfs':
    def traversal(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
        stack: MutableSequence[ICommentSubtreeTreeNode] = deque([node])
        levels = deque([0])
        while stack:
            node = cast("CommentSubtreeTreeNode[object]", stack.pop())
            level = levels.pop()
            value = node.value

            if isinstance(value, Comment):
                yield (level, value)

            if node.more:
                stack.append(node.more())
                levels.append(level)
            children = node.children
            stack.extend(reversed(children))
            levels.extend([level + 1] * len(children))

elif algo == 'bfs':
    def traversal(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
        level = 0
        queue: MutableSequence[ICommentSubtreeTreeNode] = deque([node])
        while queue:
            batch = deque(queue)
            queue.clear()

            while batch:
                node = cast("CommentSubtreeTreeNode[object]", batch.popleft())
                value = node.value

                if value is None:
                    if node.more:
                        batch.appendleft(node.more())
                    batch.extendleft(reversed(node.children))
                    continue

                if isinstance(value, Comment):
                    yield (level, value)

                queue.extend(node.children)
                if node.more:
                    queue.append(node.more())

            level += 1

else:
    raise Exception


client = redditwarp.SYNC.Client.from_access_token(access_token)
client.http.user_agent += " redditwarp.cli.comment_tree"

idn = int(
    subm_idt,
    (36 if len(subm_idt) < 8 else 10),
)
thread = client.p.comment_tree.get(idn)
if thread is None:
    print('Thread not found', file=sys.stderr)
    sys.exit(1)

subm = thread.node.value

print(f'''\
{subm.score} | {subm.title}
<{subm.id36}> by {subm.u_author_name}
Submitted at {subm.created_at.astimezone().ctime()}{' *' if subm.edited else ''}
''')

columns, _lines = shutil.get_terminal_size()

for depth, comment in traversal(thread.node):
    body_text = repr(comment.body)
    line = f"{depth*'.'} <{comment.id36}> {comment.u_author_name} | {body_text}"
    print(line[:columns])
