"""Binary search trees.

Almost every BST problem is one fact in disguise: **the in-order traversal is
sorted**. If a question mentions "k-th smallest", "validate", "closest value"
or "range sum", start by asking what the sorted order gives you.
"""

from __future__ import annotations

from collections.abc import Iterator

from .binary_trees import TreeNode


def is_valid_bst(root: TreeNode | None) -> bool:
    """Validate a BST.

    The trap is checking only `left.val < node.val < right.val` locally. That
    passes trees that are locally fine and globally wrong, because a node deep
    in the left subtree can still exceed an ancestor. Carry the *range* each
    subtree is allowed to occupy instead.
    """

    def valid(node: TreeNode | None, low: float, high: float) -> bool:
        if not node:
            return True
        if not low < node.val < high:
            return False
        return valid(node.left, low, node.val) and valid(node.right, node.val, high)

    return valid(root, float("-inf"), float("inf"))


def inorder(root: TreeNode | None) -> Iterator[int]:
    """In-order traversal as a generator — lazily sorted order.

    Being a generator matters: `kth_smallest` can stop after k values instead
    of materialising the whole traversal, which is the difference between
    O(n) and O(h + k).
    """
    stack: list[TreeNode] = []
    node = root

    while stack or node:
        while node:  # descend as far left as possible
            stack.append(node)
            node = node.left
        node = stack.pop()
        yield node.val
        node = node.right


def kth_smallest(root: TreeNode | None, k: int) -> int:
    """k-th smallest value, stopping as soon as it is found."""
    for i, value in enumerate(inorder(root), start=1):
        if i == k:
            return value
    raise ValueError("k is larger than the tree")


def insert(root: TreeNode | None, value: int) -> TreeNode:
    """Insert, returning the (possibly new) root. Duplicates ignored."""
    if not root:
        return TreeNode(value)
    if value < root.val:
        root.left = insert(root.left, value)
    elif value > root.val:
        root.right = insert(root.right, value)
    return root


def delete(root: TreeNode | None, value: int) -> TreeNode | None:
    """Delete a value, preserving the BST property.

    Three cases, and the third is the only interesting one: a node with two
    children is replaced by its in-order successor (smallest value in the
    right subtree), which is then deleted from that subtree.
    """
    if not root:
        return None

    if value < root.val:
        root.left = delete(root.left, value)
    elif value > root.val:
        root.right = delete(root.right, value)
    else:
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = delete(root.right, successor.val)

    return root


def lowest_common_ancestor(root: TreeNode | None, p: int, q: int) -> TreeNode | None:
    """LCA using the ordering — O(h), no recursion into both subtrees.

    Walk down: if both targets are smaller, go left; if both larger, go right;
    otherwise this node splits them and is the answer. Using the general
    binary-tree algorithm here throws the ordering away.
    """
    node = root
    while node:
        if p < node.val and q < node.val:
            node = node.left
        elif p > node.val and q > node.val:
            node = node.right
        else:
            return node
    return None


def build(values: list[int]) -> TreeNode | None:
    """Build a BST by repeated insertion, for testing."""
    root: TreeNode | None = None
    for value in values:
        root = insert(root, value)
    return root


CASES = [
    (([5, 3, 8, 1, 4, 7, 9], 1), 1),
    (([5, 3, 8, 1, 4, 7, 9], 4), 5),
    (([5, 3, 8, 1, 4, 7, 9], 7), 9),
    (([2, 1], 1), 1),
]


def solve(values: list[int], k: int) -> int:
    return kth_smallest(build(values), k)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected

    tree = build([5, 3, 8, 1, 4, 7, 9])
    assert list(inorder(tree)) == [1, 3, 4, 5, 7, 8, 9]
    assert is_valid_bst(tree) is True

    # Locally valid, globally wrong: 6 sits in the left subtree of 5.
    bad = TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))
    assert is_valid_bst(bad) is False
    assert is_valid_bst(None) is True

    assert list(inorder(delete(build([5, 3, 8, 1, 4, 7, 9]), 3))) == [1, 4, 5, 7, 8, 9]
    assert list(inorder(delete(build([5, 3, 8]), 5))) == [3, 8]
    assert delete(build([1]), 1) is None

    found = lowest_common_ancestor(tree, 1, 4)
    assert found is not None and found.val == 3
    found = lowest_common_ancestor(tree, 3, 9)
    assert found is not None and found.val == 5
