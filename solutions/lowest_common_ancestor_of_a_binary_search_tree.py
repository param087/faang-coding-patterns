"""Lowest Common Ancestor of a Binary Search Tree — LeetCode 235."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "lowest_common_ancestor",
    "insight": "The LCA is the single node where the two targets stop agreeing about which way to go, so walk down until the values straddle you.",
    "time": "O(h)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
The lowest node having both `p` and `q` as descendants, where a node counts as
a descendant of itself — in a **BST**, not a general binary tree.

Ask whether both nodes are guaranteed to exist (LeetCode says yes; if not, you
need a verification pass, because the descent below will happily return a node
for a value that was never in the tree). Ask whether `p` can equal `q`.

Being told it is a BST is the entire question. If you answer with the
[general-tree recursion](../../solutions/lowest-common-ancestor-of-a-binary-tree/)
you have given a correct O(n) answer to an O(h) problem, and the follow-up will
be "now use the ordering".
""",
        ),
        (
            "The insight",
            """
Start at the root and ask which way each target lies. While **both** are on the
same side, the current node cannot be the answer — the real meeting point is
deeper — so step that way.

The moment the two disagree, or one of them **is** the current node, you have
found it:

- `p.val < node.val < q.val` (in either order) — the split point. The two
  targets are in different subtrees, so no node below can contain both.
- `node.val == p.val` or `== q.val` — that node is an ancestor of itself, and
  the other target is somewhere below it.

Both conditions collapse into one loop: keep going while both values are
strictly on the same side. No recursion, no parent pointers, O(1) space, and
the first node that fails the test is the answer.

There is no backtracking anywhere, which is what buys O(h) instead of O(n).
""",
        ),
        (
            "Edge cases",
            """
- **One node is the ancestor of the other** — handled without a special case,
  because the loop stops as soon as `node.val` equals either target. This is
  the case most hand-written conditionals get wrong.
- **`p` and `q` given in either order** — do not assume `p.val < q.val`. Either
  normalise with `lo, hi = sorted(...)` first, or write the condition
  symmetrically. Assuming an order and then feeding it `(8, 2)` is the standard
  failure.
- **A target not in the tree** — the descent still terminates and returns some
  node, silently wrong. If existence is not guaranteed, search for both first.
- **Root is the answer** — happens the moment the targets sit in opposite
  subtrees of the root; the loop exits on iteration one.
- **Negative values** — plain comparisons, nothing special.
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


def find(root: TreeNode | None, value: int) -> TreeNode | None:
    """BST search, so the tests can hand real node references to the solution."""
    node = root
    while node and node.val != value:
        node = node.left if value < node.val else node.right
    return node


def lowest_common_ancestor(
    root: TreeNode | None, p: TreeNode, q: TreeNode
) -> TreeNode | None:
    node = root
    while node:
        # Both strictly on one side? The meeting point is deeper.
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node  # they split here, or this node *is* one of them
    return None


TREE = [6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]

CASES = [
    ((TREE, 2, 8), 6),  # split at the root
    ((TREE, 8, 2), 6),  # arguments in the other order
    ((TREE, 2, 4), 2),  # a node is its own ancestor
    ((TREE, 3, 5), 4),
    ((TREE, 0, 5), 2),
    (([2, 1], 2, 1), 2),
    (([0, -3, 9, -10, None, 5], -10, 5), 0),  # negatives
    ((TREE, 2, 11), None),  # target not present
]


def solve(values: list[int | None], a: int, b: int) -> int | None:
    root = from_level_order(values)
    p, q = find(root, a), find(root, b)
    if p is None or q is None:
        return None
    found = lowest_common_ancestor(root, p, q)
    return found.val if found else None
