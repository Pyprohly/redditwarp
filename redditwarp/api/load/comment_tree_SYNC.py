
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Mapping, Sequence, Dict, List
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ...models.more_comments_SYNC import MoreComments

from .comment_SYNC import load_comment
from .submission_SYNC import load_submission
from ...models.comment_tree_SYNC import CommentTreeNode, SubmissionCommentTreeNode
from ...models.comment_thread_SYNC import CommentThread
from ...models.more_comments_SYNC import ContinueThisThread, LoadMoreComments

def load_more_comments(
    d: Mapping[str, Any],
    client: Client,
    submission_id36: str,
    sort: Optional[str],
) -> MoreComments:
    _, _, comment_id36 = d['parent_id'].partition('_')
    go_deeper = d['id'] == '_'
    if go_deeper:
        return ContinueThisThread(
            submission_id36,
            comment_id36,
            sort,
            d=d,
            client=client,
        )
    return LoadMoreComments(
        submission_id36,
        comment_id36,
        sort,
        d['children'],
        d['count'],
        d=d,
        client=client,
    )

def load_topic_thread(d: Any, client: Client, sort: Optional[str]) -> CommentThread:
    def f(d: Any, client: Client, submission_id36: str, sort: Optional[str]) -> CommentTreeNode:
        value = load_comment(d, client)
        nodes = []
        more = None

        replies_data = d['replies']
        if replies_data:
            children_data = replies_data['data']['children'].copy()
            if children_data:
                m = children_data[-1]
                if m['kind'] == 'more':
                    children_data.pop()
                    more = load_more_comments(
                        m['data'],
                        client,
                        submission_id36,
                        sort,
                    )

            for m in children_data:
                comment_data = m['data']
                node = f(comment_data, client, submission_id36, sort)
                nodes.append(node)

        return CommentTreeNode(value, nodes, more)

    submission_data = d[0]['data']['children'][0]['data']
    submission_id36: str = submission_data['id']

    value = load_submission(submission_data, client)
    nodes = []
    more = None

    children_data = d[1]['data']['children'].copy()
    if children_data:
        m = children_data[-1]
        if m['kind'] == 'more':
            children_data.pop()
            more = load_more_comments(
                m['data'],
                client,
                submission_id36,
                sort,
            )

    for m in children_data:
        comment_data = m['data']
        node = f(comment_data, client, submission_id36, sort)
        nodes.append(node)

    root = SubmissionCommentTreeNode(value, nodes, more)
    return CommentThread(root, sort)

def load_more_children(d: Any, client: Client, link_id: str, sort: Optional[str]) -> Sequence[CommentTreeNode]:
    roots: List[CommentTreeNode] = []
    node_lookup: Dict[str, CommentTreeNode] = {}
    more_lookup: Dict[str, Optional[MoreComments]] = {}
    chil_lookup: Dict[str, List[CommentTreeNode]] = {}

    elements = d['json']['data']['things']
    for m in elements:
        kind = m['kind']
        if kind == 'more':
            continue
        data = m['data']
        id_ = data['name']
        parent_id = data['parent_id']

        value = load_comment(data, client)
        children: List[CommentTreeNode] = []
        node_lookup[id_] = CommentTreeNode(value, children, None)
        chil_lookup[id_] = children
        more_lookup[id_] = None

    for m in elements:
        kind = m['kind']
        data = m['data']
        id_ = data['name']
        parent_id = data['parent_id']
        if kind == 'more':
            more_obj = load_more_comments(data, client, link_id, sort)
            more_lookup[parent_id] = more_obj
        else:
            node = node_lookup[id_]
            children = chil_lookup.get(parent_id, roots)
            children.append(node)

    for id_, more in more_lookup.items():
        node = node_lookup[id_]
        node.more = more

    return roots
