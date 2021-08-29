
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional, Mapping, Dict, List
if TYPE_CHECKING:
    from ...client_SYNC import Client
    from ..more_comments_SYNC import MoreComments

from ..comment_tree_SYNC import MoreCommentsTreeNode, CommentTreeNode, SubmissionTreeNode
from ..submission_comment_tree_wrapper_SYNC import SubmissionCommentTreeWrapper
from ..more_comments_SYNC import ContinueThisThread, LoadMoreComments
from .comment_SYNC import load_comment
from .submission_SYNC import load_submission

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


def load_submission_comment_tree_wrapper(d: Any, client: Client, sort: Optional[str]) -> SubmissionCommentTreeWrapper:
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

    root = SubmissionTreeNode(value, nodes, more)
    return SubmissionCommentTreeWrapper(root, sort)

def load_more_children(d: Any, client: Client, submission_id36: str, sort: Optional[str]) -> MoreCommentsTreeNode:
    node_lookup: Dict[str, CommentTreeNode] = {}
    chilren_lookup: Dict[str, List[CommentTreeNode]] = {}

    elements = d['json']['data']['things']
    for m in elements:
        kind = m['kind']
        if kind == 'more':
            continue
        data = m['data']
        id_ = data['name']
        value = load_comment(data, client)
        children: List[CommentTreeNode] = []
        node = CommentTreeNode(value, children, None)
        node_lookup[id_] = node
        chilren_lookup[id_] = children

    roots: List[CommentTreeNode] = []
    root_more = None
    for m in elements:
        kind = m['kind']
        data = m['data']
        parent_id = data['parent_id']
        if kind == 'more':
            more = load_more_comments(data, client, submission_id36, sort)
            try:
                node_lookup[parent_id].more = more
            except KeyError:
                if root_more is not None:
                    raise Exception
                root_more = more
        else:
            id_ = data['name']
            node = node_lookup[id_]
            chilren_lookup.get(parent_id, roots).append(node)

    # Use `None` for the node's value here because it's important we
    # don't allow any node to appear more than once in the tree.
    return MoreCommentsTreeNode(None, roots, root_more)
