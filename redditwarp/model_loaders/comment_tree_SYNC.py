
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Mapping
if TYPE_CHECKING:
    from ..client_SYNC import Client
    from ..models.more_comments_SYNC import MoreComments
    from ..models.comment_SYNC import Comment

from ..models.comment_tree_SYNC import MoreCommentsTreeNode, CommentTreeNode, SubmissionTreeNode
from ..models.more_comments_SYNC import ContinueThisThread, LoadMoreComments
from .comment_SYNC import load_comment
from .submission_SYNC import load_submission

def load_more_comments(
    d: Mapping[str, Any],
    client: Client,
    submission_id36: str,
    sort: str,
) -> MoreComments:
    _, _, comment_id36 = d['parent_id'].partition('_')
    go_deeper = d['id'] == '_'
    if go_deeper:
        return ContinueThisThread(
            submission_id36=submission_id36,
            comment_id36=comment_id36,
            sort=sort,
            d=d,
            client=client,
        )
    return LoadMoreComments(
        submission_id36=submission_id36,
        comment_id36=comment_id36,
        child_id36s=d['children'],
        sort=sort,
        count=d['count'],
        d=d,
        client=client,
    )


def load_submission_tree_node(d: Any, client: Client, sort: str) -> SubmissionTreeNode:
    def load_comment_tree_node(d: Any, client: Client, submission_id36: str, sort: str) -> CommentTreeNode:
        value = load_comment(d, client)
        children = []
        more = None

        replies_data = d['replies']
        if replies_data:
            elements = list(replies_data['data']['children'])
            if elements:
                m = elements[-1]
                if m['kind'] == 'more':
                    elements.pop()
                    more = load_more_comments(m['data'], client, submission_id36, sort)

                for m in elements:
                    node = load_comment_tree_node(m['data'], client, submission_id36, sort)
                    children.append(node)

        return CommentTreeNode(value, children, more)

    submission_data = d[0]['data']['children'][0]['data']
    submission_id36: str = submission_data['id']

    value = load_submission(submission_data, client)
    children = []
    more = None

    elements = list(d[1]['data']['children'])
    if elements:
        m = elements[-1]
        if m['kind'] == 'more':
            elements.pop()
            more = load_more_comments(m['data'], client, submission_id36, sort)

        for m in elements:
            node = load_comment_tree_node(m['data'], client, submission_id36, sort)
            children.append(node)

    return SubmissionTreeNode(value, children, more)


def load_more_comments_tree_node(d: Any, client: Client, submission_id36: str, sort: str) -> MoreCommentsTreeNode:
    value_lookup: dict[str, Comment] = {}
    children_lookup: dict[str, list[CommentTreeNode]] = {}
    more_lookup: dict[str, MoreComments] = {}

    elements = d['json']['data']['things']
    for m in elements:
        data = m['data']
        kind = m['kind']
        if kind == 'more':
            more = load_more_comments(data, client, submission_id36, sort)
            parent_idt = data['parent_id']
            more_lookup[parent_idt] = more
        else:
            value = load_comment(data, client)
            children: list[CommentTreeNode] = []
            idt = data['name']
            value_lookup[idt] = value
            children_lookup[idt] = children

    root_children: list[CommentTreeNode] = []
    for m in elements:
        data = m['data']
        kind = m['kind']
        if kind != 'more':
            idt = data['name']
            node = CommentTreeNode(
                value_lookup[idt],
                children_lookup[idt],
                more_lookup.pop(idt, None),
            )
            parent_idt = data['parent_id']
            children_lookup.get(parent_idt, root_children).append(node)

    root_more = None
    if more_lookup:
        root_more = more_lookup.popitem()[1]
    if more_lookup:
        raise Exception

    return MoreCommentsTreeNode(None, root_children, root_more)
