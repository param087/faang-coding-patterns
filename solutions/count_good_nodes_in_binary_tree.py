"""Count Good Nodes in Binary Tree — LeetCode 1448."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "good_nodes",
    "insight": "The only thing a node needs from its ancestors is the maximum seen on the way down, so push that down instead of returning anything up.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
A node is *good* if no node on the path from the root to it holds a **strictly
greater** value. Count them.

The root is always good. Ask about ties — a node equal to the running maximum
**is** good, so the test is `>=`, not `>`. And ask the value range: LeetCode
allows negatives down to −10⁴, which rules out the lazy `best = 0` seed.
""",
        ),
        (
            "The insight",
            """
Tree recursions split into two families, and knowing which one you are in is
most of the work:

- **Bottom-up (synthesised)** — the child computes something the parent
  combines: heights, diameters, subtree sums.
- **Top-down (inherited)** — the parent hands the child everything it needs to
  decide for itself: this problem, valid-BST bounds, root-to-leaf sums.

Here the entire ancestor path collapses into **one number**, the maximum seen so
far. A node does not need the list of ancestors, or their order, or their count.
So pass `max(best, node.val)` down, decide locally, and let the return value do
nothing but add up the counts.

```
walk(node, best):
    if node is None: return 0
    good = 1 if node.val >= best else 0
    best = max(best, node.val)
    return good + walk(node.left, best) + walk(node.right, best)
```

O(1) inherited state, so an explicit stack of `(node, best)` pairs converts this
to iterative in about four lines if recursion depth is a concern — the constraint
allows 10⁵ nodes, and a degenerate chain of that depth blows Python's default
1000-frame limit.
""",
        ),
        (
            "Edge cases",
            """
- **Seeding with 0 instead of the root value.** On `[-1,-2,-3]` the correct
  answer is 1 (only the root), but a zero seed rejects the root itself and
  returns 0. Seed with `root.val` — or negative infinity, but then handle the
  empty tree first.
- **Ties.** `[2,null,2,null,2]` is 3 good nodes, not 1. `>` instead of `>=` is
  the single most common wrong character in this problem.
- **Empty tree** → 0, and the seed expression must not touch `root.val` before
  that check.
- **Nothing is pruned.** Even a node whose whole subtree sits below the running
  maximum has to be visited, because *its* descendants may exceed it — but they
  are compared against the ancestor maximum, not against it. There is no
  shortcut; every node is examined exactly once and that is already optimal.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def good_nodes(root: TreeNode | None) -> int:
    if root is None:
        return 0

    def walk(node: TreeNode | None, best: int) -> int:
        if node is None:
            return 0
        good = 1 if node.val >= best else 0  # >= : a tie is still good
        best = max(best, node.val)
        return good + walk(node.left, best) + walk(node.right, best)

    return walk(root, root.val)  # seed with the root, not 0 — values can be negative


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


CASES = [
    (([3, 1, 4, 3, None, 1, 5],), 4),
    (([3, 3, None, 4, 2],), 3),
    (([1],), 1),
    (([],), 0),
    (([-1, -2, -3],), 1),  # a `best = 0` seed answers 0 here
    (([2, None, 2, None, 2],), 3),  # ties count
    (([9, 3, None, 1],), 1),  # strictly decreasing spine
    (([1, 2, 3],), 3),  # increasing: everything is good
]


def solve(values: list[int | None]) -> int:
    return good_nodes(from_level_order(values))
