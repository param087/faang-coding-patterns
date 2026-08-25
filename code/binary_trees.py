"""Binary tree traversal and recursion.

One question unlocks almost every tree problem: *what does a node return to
its parent?* Answer that and the recursion writes itself. When the answer the
parent needs differs from the answer the problem wants, use a nonlocal
accumulator — that mismatch is the whole difficulty of diameter and max path
sum.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def from_level_order(values: list[int | None]) -> TreeNode | None:
    """Build a tree from LeetCode's level-order list, for testing."""
    if not values or values[0] is None:
        return None

    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values):
            value = values[i]
            i += 1
            if value is not None:
                node.left = TreeNode(value)
                queue.append(node.left)
        if i < len(values):
            value = values[i]
            i += 1
            if value is not None:
                node.right = TreeNode(value)
                queue.append(node.right)
    return root


def max_depth(root: TreeNode | None) -> int:
    """Height of the tree. The simplest instance of the template."""
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def level_order(root: TreeNode | None) -> list[list[int]]:
    """BFS, grouped by level.

    Capturing `len(queue)` before the inner loop is what separates the levels.
    Without it you get a flat traversal, because the queue grows while you
    are draining it.
    """
    if not root:
        return []

    levels: list[list[int]] = []
    queue = deque([root])

    while queue:
        level: list[int] = []
        for _ in range(len(queue)):  # snapshot: exactly this level
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)

    return levels


def diameter(root: TreeNode | None) -> int:
    """Longest path between any two nodes, measured in edges.

    The mismatch that makes this feel hard: the parent needs the *depth*
    below a node, but the answer is the best *path through* a node. So the
    recursion returns depth and records the answer on the side.
    """
    best = 0

    def depth(node: TreeNode | None) -> int:
        nonlocal best
        if not node:
            return 0
        left = depth(node.left)
        right = depth(node.right)
        best = max(best, left + right)  # path through this node
        return 1 + max(left, right)  # what the parent can use

    depth(root)
    return best


def max_path_sum(root: TreeNode | None) -> int:
    """Largest sum along any downward-then-upward path.

    Same shape as diameter with two extra wrinkles: negative branches are
    clamped to zero because you may decline to take them, and the path a
    parent can extend may only use *one* child.
    """
    best = float("-inf")

    def gain(node: TreeNode | None) -> int:
        nonlocal best
        if not node:
            return 0
        left = max(gain(node.left), 0)  # decline a negative branch
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)
        return node.val + max(left, right)  # parent can only use one side

    gain(root)
    return int(best)


def lowest_common_ancestor(
    root: TreeNode | None, p: TreeNode, q: TreeNode
) -> TreeNode | None:
    """LCA in a plain binary tree (no BST ordering available).

    Returns a target if it is found in this subtree, otherwise whichever side
    found something. A node that hears back from *both* sides is the answer —
    which is why the whole function is six lines.
    """
    if not root or root is p or root is q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root
    return left or right


CASES = [
    (([3, 9, 20, None, None, 15, 7],), 3),
    (([1, None, 2],), 2),
    (([1],), 1),
    (([],), 0),
]


def solve(values: list[int | None]) -> int:
    return max_depth(from_level_order(values))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected

    assert level_order(from_level_order([3, 9, 20, None, None, 15, 7])) == [[3], [9, 20], [15, 7]]
    assert level_order(None) == []

    assert diameter(from_level_order([1, 2, 3, 4, 5])) == 3
    assert diameter(from_level_order([1, 2])) == 1
    assert diameter(None) == 0

    assert max_path_sum(from_level_order([1, 2, 3])) == 6
    assert max_path_sum(from_level_order([-10, 9, 20, None, None, 15, 7])) == 42
    assert max_path_sum(from_level_order([-3])) == -3

    root = from_level_order([3, 5, 1, 6, 2, 0, 8])
    assert root is not None and root.left is not None and root.right is not None
    found = lowest_common_ancestor(root, root.left, root.right)
    assert found is not None and found.val == 3
    found = lowest_common_ancestor(root, root.left, root.left.right)
    assert found is not None and found.val == 5  # a node is its own ancestor
