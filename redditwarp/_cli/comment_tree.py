
from __future__ import annotations
from typing import TYPE_CHECKING, MutableSequence, Iterator, Callable
if TYPE_CHECKING:
    from redditwarp.models.comment_tree_SYNC import CommentSubtreeTreeNode, MoreCommentsTreeNode

###
ALGORITHM_CHOICES = (
    'dfs',
    'dfs0',
    'dfs1',
    'dfs2',
    'bfs',
    'bfs1',
    'bfs2',
)
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
add('--sort', dest='sort', choices=COMMENT_SORT_CHOICES, default='confidence')
args = parser.parse_args()
###;

import sys
import shutil
from collections import deque

import redditwarp.SYNC
from redditwarp.util.extract_id_from_url import extract_submission_id_from_url
from redditwarp.models.comment_SYNC import Comment

access_token: str = args.access_token_opt or ''
target: str = args.target or args.target_opt or input('Target: ')
algo: str = args.algo
sort: str = args.sort
base: int = args.base_opt


# A recursive DFS. The algorithm looks clean and performs well, except that Python
# limits the maximum function recursion depth to 1000, so if you have a very deep
# comment tree you’ll have to use an iterative approach.
def depth_first_recursive(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
    def traverse(root: CommentSubtreeTreeNode[object], level: int = 0) -> Iterator[tuple[int, Comment]]:
        value = root.value
        if isinstance(value, Comment):
            yield (level, value)

        for child in root.children:
            yield from traverse(child, level + 1)

        if root.more:
            yield from traverse(root.more(), level)

    return traverse(node)

# An iterative DFS that is functionally equivalent to the recursive version but is
# slightly inaccurate because the `MoreComments` callables are evaluated before the
# child nodes are processed. It’s undesirable because for a display script it has the
# effect of feeling slower and looking more jittery.
def depth_first_iterative_1(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
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

# This version is more algorithmically accurate to the recursive one but at the cost of
# looking messier.
def depth_first_iterative_2(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
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

# This BFS traversal evaluates the `MoreComments` callables before processing the
# children which, we’ve established is undesirable because it feels slow.
def breadth_first_1(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
    level = 0
    queue: MutableSequence[CommentSubtreeTreeNode[object]] = deque([node])
    while queue:
        batch = deque(queue)
        queue.clear()
        while batch:
            node = batch.popleft()
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

# A BFS that processes all children before evaluating `MoreComments` callables.
# Algorithmically better but programmatically uglier.
def breadth_first_2(node: CommentSubtreeTreeNode[object]) -> Iterator[tuple[int, Comment]]:
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


traversal = {
    'dfs': depth_first_iterative_2,
    'dfs0': depth_first_recursive,
    'dfs1': depth_first_iterative_1,
    'dfs2': depth_first_iterative_2,
    'bfs': breadth_first_2,
    'bfs1': breadth_first_1,
    'bfs2': breadth_first_2,
}[algo]

client = (
    redditwarp.SYNC.Client.from_access_token(access_token)
    if access_token else
    redditwarp.SYNC.Client()
)

client.http.set_user_agent(client.http.get_user_agent() + " redditwarp.cli.comment_tree")

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

tree_node = client.p.comment_tree.get(idn, sort=sort)
if tree_node is None:
    print('Submission not found', file=sys.stderr)
    sys.exit(1)

m = tree_node.value

print(f'''\
{m.permalink}
{m.id36}+ ^:{m.score} | {m.title}
Submitted {m.created_at.astimezone().ctime()}{' *' if m.is_edited else ''} \
by u/{m.author_name} to r/{m.subreddit.name}
''')

columns, _lines = shutil.get_terminal_size()

for depth, comment in traversal(tree_node):
    c = comment
    body_text = repr(c.body)
    line = f"{depth*'.'} u/{c.author_name} | {body_text}"
    print(line[:columns])
