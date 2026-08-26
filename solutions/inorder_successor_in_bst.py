"""Inorder Successor in BST — LeetCode 285."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "inorder_successor",
    "insight": "The successor is the last node you turned left at on the way down — one descent, no parent pointers, no traversal.",
    "time": "O(h) — O(log n) balanced, O(n) for a chain",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Premium problem, so the statement is not public. In my own words: given the
root of a BST and one of its nodes `p`, return the node that comes immediately
after `p` in an in-order traversal, or nothing if `p` is the largest value in
the tree.

Ask three things before writing:

- **A node reference or just a value?** The real signature hands you the node.
  That matters — if it only gave you a value, duplicates would make the target
  ambiguous.
- **Do nodes carry parent pointers?** Usually not. If they do (that is
  LeetCode 510) the problem changes completely — you climb instead of descend.
- **Is `p` guaranteed present?** Say yes; the descent below is unaffected
  either way, which is a nice property to point out.

The harness here locates the node by value, since a BST built from distinct
values makes that unambiguous.
""",
        ),
        (
            "The insight",
            """
In-order order is sorted order, so "successor" just means **the smallest value
strictly greater than `p.val`**. That reframes a traversal question into a
search question.

The naive decomposition is two cases:

- `p` has a right child → the answer is the leftmost node of that right
  subtree;
- `p` has no right child → the answer is the lowest ancestor whose *left*
  subtree contains `p`, and with no parent pointers you cannot reach it from
  `p` at all.

You do not need either case. One descent from the root covers both: whenever
the current node's value is greater than `p.val`, record it as a candidate and
go **left**; otherwise go **right**. The last candidate recorded is the answer.

Each left turn tightens the upper bound on the answer, so the final candidate
is the tightest one — and if you never turned left, `p` is the maximum and
there is no successor.

O(h) time, O(1) space. The stack-based in-order traversal that stops one step
past `p` is also correct but costs O(n) time and O(h) space, and it is the
version that gets follow-up pressure.
""",
        ),
        (
            "Follow-ups",
            """
- **In-order predecessor** — mirror every comparison: record when the node is
  *smaller* than the target, then go right.
- **Successor with parent pointers (LeetCode 510)** — if `p` has a right
  child, take its leftmost node; otherwise climb until you arrive at a node
  from its left child. Still O(h), and now genuinely local to `p`.
- **Successor in a plain binary tree** — no ordering means no pruning, so you
  are back to a full in-order traversal that remembers the previous node.
- **The k-th successor, repeatedly** — augment each node with its subtree size
  and you get order statistics in O(h) per query instead of O(k·h).
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


def inorder_successor(root: TreeNode | None, target: int) -> TreeNode | None:
    """The real signature takes a node `p`; only `p.val` is ever used."""
    successor: TreeNode | None = None
    node = root

    while node:
        if node.val > target:
            successor = node  # a candidate — something smaller may still beat it
            node = node.left  # every left turn tightens the upper bound
        else:
            node = node.right

    return successor  # None means the target was the maximum


CASES = [
    (([2, 1, 3], 1), 2),
    (([2, 1, 3], 3), None),  # the maximum has no successor
    (([5, 3, 6, 2, 4, None, None, 1], 3), 4),  # right child exists
    (([5, 3, 6, 2, 4, None, None, 1], 4), 5),  # successor is an ancestor
    (([5, 3, 6, 2, 4, None, None, 1], 1), 2),  # deepest leaf, ancestor answer
    (([20, 10, 30, 5, 15, 25, 35, None, None, 12, 17], 17), 20),  # ancestor three levels up
    (([1], 1), None),
    (([], 1), None),
]


def solve(values: list[int | None], target: int) -> int | None:
    successor = inorder_successor(from_level_order(values), target)
    return successor.val if successor else None
