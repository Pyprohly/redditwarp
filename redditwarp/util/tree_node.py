
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Sequence

T = TypeVar('T')
TChild = TypeVar('TChild')

class Node(Generic[T]):
    def __init__(self, value: T):
        self.value = value

class TreeNode(Node[T], Generic[T, TChild]):
    pass


class BinaryTreeNode(TreeNode[T, TChild]):
    def __init__(self,
        value: T,
        left: Optional[TChild],
        right: Optional[TChild],
    ):
        super().__init__(value)
        self.left = left
        self.right = right

__bound = 'BinaryTreeNode[T, TBinaryTreeNode]'
TBinaryTreeNode = TypeVar('TBinaryTreeNode', bound=BinaryTreeNode)  # type: ignore[type-arg]


class GeneralTreeNode(TreeNode[T, TChild]):
    def __init__(self,
        value: T,
        children: Sequence[TChild],
    ):
        super().__init__(value)
        self.children = children

__bound = 'GeneralTreeNode[T, TGeneralTreeNode]'
TGeneralTreeNode = TypeVar('TGeneralTreeNode', bound=GeneralTreeNode)  # type: ignore[type-arg]
