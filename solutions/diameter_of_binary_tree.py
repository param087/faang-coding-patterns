"""Diameter of Binary Tree — LeetCode 543."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "diameter_of_binary_tree",
    "insight": "The parent needs a depth; the answer is a bending path. Return the former, accumulate the latter on the side.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
The length of the longest path between any two nodes, measured in **edges**.
The path need not pass through the root.

Ask this first: **edges or nodes?** On LeetCode it is edges, so a two-node tree
has diameter 1. Getting it backwards is an off-by-one on every test case.
""",
        ),
        (
            "The naive attempt",
            """
For every node, compute left height plus right height — each height costing
O(n). That is O(n²).

Say it, then improve it. It also frames the fix nicely: you are computing
heights over and over, and one traversal already has them.
""",
        ),
        (
            "The insight",
            """
Here is the structural point, and it unlocks a whole tier of tree problems:

> **What the parent needs is different from what the problem asks for.**

The parent can only extend a path *downward*, so what it needs is the **depth**
below a node. But the answer is the longest path *through* a node, which bends
and cannot be extended upward.

Two different quantities. So the recursion **returns the depth** and
**accumulates the answer** in a `nonlocal`.

Once you see this, Binary Tree Maximum Path Sum is the same function with
values instead of counts.
""",
        ),
        (
            "Dry run",
            """
`[1,2,3,4,5]`.

- At node 2: left height 1, right height 1 → bending path of length **2**.
- At node 1: left height 2, right height 1 → bending path of length **3**.

Answer 3, which is the path 4→2→1→3. Note it does not run through the deepest
leaf in a straight line — that is why a single "height" answer is not enough.
""",
        ),
        (
            "Follow-ups",
            """
- **Binary Tree Maximum Path Sum** — same shape, plus two wrinkles: clamp
  negative branches to zero, and seed the best at negative infinity.
- **Diameter of an N-ary tree** — take the two largest child depths instead of
  left and right.
- **Diameter of a general graph (tree)** — two BFS passes: farthest node from
  anywhere, then farthest from that node.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def from_level_order(values: list[int | None]) -> TreeNode | None:
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        for side in ("left", "right"):
            if i >= len(values):
                break
            value = values[i]
            i += 1
            if value is not None:
                child = TreeNode(value)
                setattr(node, side, child)
                queue.append(child)
    return root


def diameter_of_binary_tree(root: TreeNode | None) -> int:
    best = 0

    def depth(node: TreeNode | None) -> int:
        nonlocal best
        if not node:
            return 0
        left = depth(node.left)
        right = depth(node.right)
        best = max(best, left + right)  # the path bending through this node
        return 1 + max(left, right)  # what the parent can actually extend

    depth(root)
    return best


CASES = [
    (([1, 2, 3, 4, 5],), 3),
    (([1, 2],), 1),
    (([1],), 0),
    (([],), 0),
    (([1, 2, None, 3, None, 4, None, 5],), 4),
]


def solve(values: list[int | None]) -> int:
    return diameter_of_binary_tree(from_level_order(values))
