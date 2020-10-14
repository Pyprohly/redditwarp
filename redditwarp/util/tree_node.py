
from __future__ import annotations
from typing import TypeVar, Generic, Optional, Sequence

E = TypeVar('E')

class Node(Generic[E]):
    def __init__(self, value: E):
        self.value = value


class IBinaryTreeNode:
    pass

TBinaryTreeNodeInterface = TypeVar('TBinaryTreeNodeInterface', bound=IBinaryTreeNode)

class BinaryTreeNode(IBinaryTreeNode, Node[E], Generic[TBinaryTreeNodeInterface, E]):
    def __init__(self,
        value: E,
        left: Optional[TBinaryTreeNodeInterface],
        right: Optional[TBinaryTreeNodeInterface],
    ):
        super().__init__(value)
        self.left = left
        self.right = right

__bound = 'BinaryTreeNode[TBinaryTreeNode, E]'
TBinaryTreeNode = TypeVar('TBinaryTreeNode', bound=BinaryTreeNode)  # type: ignore[type-arg]


class IGeneralTreeNode:
    pass

TGeneralTreeNodeInterface = TypeVar('TGeneralTreeNodeInterface', bound=IGeneralTreeNode)

class GeneralTreeNode(IGeneralTreeNode, Node[E], Generic[TGeneralTreeNodeInterface, E]):
    def __init__(self,
        value: E,
        children: Sequence[TGeneralTreeNodeInterface],
    ):
        super().__init__(value)
        self.children = children

__bound = 'GeneralTreeNode[TGeneralTreeNode, E]'
TGeneralTreeNode = TypeVar('TGeneralTreeNode', bound=GeneralTreeNode)  # type: ignore[type-arg]
