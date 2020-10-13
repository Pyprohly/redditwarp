
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Sequence

E = TypeVar('E')

class Node(Generic[E]):
    def __init__(self, value: E):
        self.value = value

__bound = 'BinaryTreeNode[TBinaryTreeNode, E]'
TBinaryTreeNode = TypeVar('TBinaryTreeNode', bound='BinaryTreeNode')  # type: ignore[type-arg]

class BinaryTreeNode(Node[E], Generic[TBinaryTreeNode, E]):
    def __init__(self,
        value: E,
        left: Optional[TBinaryTreeNode],
        right: Optional[TBinaryTreeNode],
    ):
        super().__init__(value)
        self.left = left
        self.right = right

__bound = 'GeneralTreeNode[TGeneralTreeNode, E]'
TGeneralTreeNode = TypeVar('TGeneralTreeNode', bound='GeneralTreeNode')  # type: ignore[type-arg]

class GeneralTreeNode(Node[E], Generic[TGeneralTreeNode, E]):
    def __init__(self,
        value: E,
        children: Sequence[TGeneralTreeNode],
    ):
        super().__init__(value)
        self.children = children
