
from __future__ import annotations
from typing import TYPE_CHECKING, MutableSequence, cast, Iterator
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import ICommentSubtreeTreeNode, CommentSubtreeTreeNode, T

import sys
import shutil
from collections import deque

import redditwarp
from redditwarp.util.extract_id_from_url import extract_submission_id_from_url
from redditwarp.models.comment_SYNC import Comment

ALGORITHM_CHOICES = {
    'iterative_depth_first_search': 'dfs',
    'depth_first_search': 'dfs',
    'dfs': 'dfs',
    'recursive_depth_first_search': 'recursive_depth_first_search',
    'breadth_first_search': 'bfs',
    'bfs': 'bfs',
}
COMMENT_SORT_CHOICES = 'confidence top new controversial old random qa live'.split()

import argparse
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter): pass
parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
parser._optionals.title = __import__('gettext').gettext('named arguments')
add = parser.add_argument
add('access_token', nargs='?')
add('target', nargs='?')
add('--access-token', metavar='ACCESS_TOKEN', dest='access_token_opt', help=argparse.SUPPRESS)
add('--target', metavar='TARGET', dest='target_opt', help=argparse.SUPPRESS)
add('--algo', '--algorithm', choices=ALGORITHM_CHOICES, default='dfs', dest='algo', metavar='')
add('--comment-sort', dest='comment_sort', choices=COMMENT_SORT_CHOICES)
args = parser.parse_args()

access_token: str = args.access_token or args.access_token_opt or input('Access token: ')
target: str = args.target or args.target_opt or input('Target: ')
chosen_algo: str = args.algo
comment_sort: str = args.comment_sort


def recursive_depth_first_search(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
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

def depth_first_search(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
    stack: MutableSequence[ICommentSubtreeTreeNode] = deque([node])
    levels = deque([0])
    while stack:
        node = cast("CommentSubtreeTreeNode[object]", stack.pop())
        value = node.value
        level = levels.pop()

        if isinstance(value, Comment):
            yield (level, value)

        if node.more:
            stack.append(node.more())
            levels.append(level)

        cl = node.children
        stack.extend(reversed(cl))
        levels.extend([level + 1] * len(cl))

def breadth_first_search(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
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


algo = ALGORITHM_CHOICES[chosen_algo]
traversal = {
    'recursive_depth_first_search': recursive_depth_first_search,
    'dfs': depth_first_search,
    'bfs': breadth_first_search,
}[algo]

client = redditwarp.SYNC.Client.from_access_token(access_token)
client.http.user_agent += " redditwarp.cli.comment_tree"

idn = 0
length = len(target)
if length < 8:
    idn = int(target, 36)
elif length < 12:
    idn = int(target, 10)
else:
    idn = extract_submission_id_from_url(target)

tree = client.p.comment_tree.get(idn)
if tree is None:
    print('Submission not found', file=sys.stderr)
    sys.exit(1)

root = tree.node
submission = m = root.value

print(f'''\
{m.permalink}
{m.score} :: {m.title}
#{m.id36} by u/{m.author_name} to r/{m.subreddit.name}
Submitted at {m.created_at.astimezone().ctime()}{' *' if m.edited else ''}
''')

columns, _lines = shutil.get_terminal_size()

for depth, comment in traversal(root):
    c = comment
    body_text = repr(c.body)
    line = f"{depth*'.'} u/{c.author_name} | {body_text}"
    print(line[:columns])
