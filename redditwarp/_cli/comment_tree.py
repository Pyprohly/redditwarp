
from __future__ import annotations
from typing import TYPE_CHECKING, MutableSequence, cast, Iterator
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import ICommentSubtreeTreeNode, CommentSubtreeTreeNode, T

###
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
add('target', nargs='?')
add('--access-token', metavar='ACCESS_TOKEN', dest='access_token_opt')
add('--target', metavar='TARGET', dest='target_opt', help=argparse.SUPPRESS)
add('--base', metavar='N', dest='base_opt', type=int, default=36)
add('--algo', '--algorithm', choices=ALGORITHM_CHOICES, default='dfs', dest='algo', metavar='')
add('--comment-sort', dest='comment_sort', choices=COMMENT_SORT_CHOICES)
args = parser.parse_args()
###;

import sys
import shutil
from collections import deque

import redditwarp
from redditwarp.util.extract_id_from_url import extract_submission_id_from_url
from redditwarp.models.comment_SYNC import Comment

access_token: str = args.access_token_opt or ''
target: str = args.target or args.target_opt or input('Target: ')
chosen_algo: str = args.algo
comment_sort: str = args.comment_sort
base: int = args.base_opt


def recursive_depth_first_search(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
    def dfs(
        root: CommentSubtreeTreeNode[T],
        level: int = 0,
    ) -> Iterator[tuple[int, Comment]]:
        value = root.value
        if isinstance(value, Comment):
            yield (level, value)

        for child in root.children:
            yield from dfs(child, level + 1)

        if root.more:
            yield from dfs(root.more(), level)

    return dfs(cast("CommentSubtreeTreeNode[object]", node))

def depth_first_search(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
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

        stack.extend(reversed(node.children))
        levels.extend([level + 1] * len(node.children))

def breadth_first_search(node: ICommentSubtreeTreeNode) -> Iterator[tuple[int, Comment]]:
    level = 0
    queue: MutableSequence[ICommentSubtreeTreeNode] = deque([node])
    while queue:
        batch = deque(queue)
        queue.clear()
        while batch:
            node = cast("CommentSubtreeTreeNode[object]", batch.popleft())
            if node.value is None:
                if node.more:
                    batch.appendleft(node.more())
                batch.extendleft(reversed(node.children))
                continue

            value = node.value
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

client = (
    redditwarp.SYNC.Client.from_access_token(access_token)
    if access_token else
    redditwarp.SYNC.Client()
)

client.http.user_agent += " redditwarp.cli.comment_tree"

idn = 0
if target.isalnum():
    try:
        idn = int(target, base)
    except ValueError as e:
        print(f'{e.__class__.__name__}: {e}', file=sys.stderr)
        sys.exit(1)
else:
    try:
        idn = extract_submission_id_from_url(target)
    except ValueError:
        print('Could not extract comment ID from URL.', file=sys.stderr)
        sys.exit(1)

tree_node = client.p.comment_tree.get(idn, sort=comment_sort)
if tree_node is None:
    print('Submission not found', file=sys.stderr)
    sys.exit(1)

m = tree_node.value

print(f'''\
{m.permalink}
{m.id36}+ | {m.score} :: {m.title}
Submitted {m.created_at.astimezone().ctime()}{' *' if m.is_edited else ''} \
by u/{m.author_name} to r/{m.subreddit.name}
''')

columns, _lines = shutil.get_terminal_size()

for depth, comment in traversal(tree_node):
    c = comment
    body_text = repr(c.body)
    line = f"{depth*'.'} u/{c.author_name} | {body_text}"
    print(line[:columns])
