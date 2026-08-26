"""Closest Binary Search Tree Value — LeetCode 270."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "closest_value",
    "insight": "The search path for the target already contains both its predecessor and its successor, so one descent sees every candidate.",
    "time": "O(h) — O(log n) balanced, O(n) for a chain",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Premium problem, so the statement is not public. In my own words: given a BST
and a **floating-point** target, return the value in the tree closest to it.
If two values are equally close, return the smaller one.

Two clarifiers that are actually load-bearing:

- **The target is a real number, not a node value.** It usually is not in the
  tree at all, so this is a nearest-neighbour query, not a lookup.
- **The tie rule.** "Return the smaller" is easy to miss and it is exactly what
  the hidden tests check; a target sitting halfway between two node values is
  the canonical failing case.

Node count is at least 1 in the real constraints, but a null-safe version costs
nothing, so the code here returns nothing for an empty tree.
""",
        ),
        (
            "The insight",
            """
The closest value is either the largest value ≤ target or the smallest value ≥
target — the target's predecessor and successor in sorted order. Nothing else
can be nearer.

The fact that makes this O(h): **the ordinary BST search path for the target
passes through both of them.** Every node you visit narrows the interval the
target lives in, and the two eventual boundary values are the two candidates.
So you never need a traversal, a heap, or a sorted list — descend once, and
keep the best value seen along the way.

```
node.val > target → go left; node.val <= target → go right
```

Comparing every visited node against the running best is not wasteful: it is
what removes the need to reason about which of the two boundaries you are
currently standing on.

O(h) time and O(1) space. The full in-order traversal — O(n) time, O(h) space —
is correct and is the answer that gets asked "can you do better?".
""",
        ),
        (
            "Ties, and the exactness trap",
            """
The tie rule needs an explicit second clause:

```python
better = distance < best_distance or (distance == best_distance and node.val < best)
```

Without it you keep whichever tied value you happened to meet first, which on
`[2,1,3]` with target `1.5` is the root `2` — the answer is `1`. The descent is
guaranteed to see both tied values because, as above, both boundaries lie on
the search path, so the `<` comparison is enough to break the tie correctly.

The subtler point, worth mentioning rather than coding around: `distance ==
best_distance` is a float equality test. With integer node values and a target
that is an exact binary fraction it is exact, and LeetCode's targets are. For
arbitrary doubles you would compare `node.val + best` against `2 * target`
instead, which keeps the comparison in a domain where the arithmetic is exact.

Follow-up to expect: **Closest BST Value II** — the k closest values. That one
is not the same trick; it is an in-order traversal feeding a size-k sliding
window (or two stacks running predecessor/successor outward in a merge), which
is O(h + k) rather than another single descent.
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


def closest_value(root: TreeNode | None, target: float) -> int | None:
    if root is None:
        return None

    best = root.val
    node: TreeNode | None = root

    while node:
        distance = abs(node.val - target)
        best_distance = abs(best - target)
        # The second clause is the tie rule: equally close -> take the smaller.
        if distance < best_distance or (distance == best_distance and node.val < best):
            best = node.val
        # Both candidates lie on this path, so a plain search descent suffices.
        node = node.left if target < node.val else node.right

    return best


CASES = [
    (([4, 2, 5, 1, 3], 3.714286), 4),
    (([2, 1, 3], 1.5), 1),  # exact tie -> the smaller value
    (([2, 1, 3], 2.5), 2),  # exact tie again, this time root vs right child
    (([10, 5, 15, 3, 7, 13, 18], 8.4), 7),  # nearest is the predecessor
    (([10, 5, 15, 3, 7, 13, 18], -100.0), 3),  # target below the minimum
    (([10, 5, 15, 3, 7, 13, 18], 100.0), 18),  # target above the maximum
    (([1], 4.428571), 1),
    (([], 3.0), None),
]


def solve(values: list[int | None], target: float) -> int | None:
    return closest_value(from_level_order(values), target)
