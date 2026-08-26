"""Minimum Absolute Difference in BST — LeetCode 530."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "get_minimum_difference",
    "insight": "The closest pair in a sorted sequence is always adjacent, so only consecutive in-order neighbours can win.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
The smallest absolute difference between the values of **any two distinct
nodes** in a BST — any two, not just related ones. LeetCode 783 is the same
problem with a different title.

Ask whether values can repeat. If they can, the answer is trivially 0 and the
problem is testing whether you noticed. LeetCode guarantees distinct values
here, and at least two nodes.
""",
        ),
        (
            "The insight",
            """
Two facts, in order:

1. In a **sorted** sequence, the closest pair is always **adjacent**. Any
   non-adjacent pair has something in between, which is at least as close to
   both. So of the n(n-1)/2 pairs, only n-1 can possibly win.
2. The in-order traversal of a BST **is** that sorted sequence.

Together: traverse in-order, keep the previously visited value, and take the
minimum of consecutive differences. One pass, O(n), and no comparison ever
looks at anything but a neighbour.

Two details worth saying:

- You never need `abs`. In-order values are non-decreasing, so
  `node.val - prev` is already the magnitude. If your code needs `abs`, your
  traversal is not in-order.
- Track the previous **value**, not the previous node, and initialise it to a
  "nothing seen yet" marker rather than 0 or infinity — with negative values,
  a 0 seed silently invents a node at the origin.
""",
        ),
        (
            "The wrong first answer",
            """
The reflex is to compare each node against its children and recurse. It looks
right, it passes small examples, and it is wrong: the closest pair need not be
parent and child.

```
      10
     /  \\
    5    20
     \\   /
      9 11
```

In-order: `5, 9, 10, 11, 20`. The true minimum is **1** (9 and 10, or 10 and
11). Every parent-child difference is at least 4, so the local check confidently
returns 4.

The other wrong answer is the O(n²) double loop over all pairs. It is correct,
and at n = 10⁴ it is 5 × 10⁷ comparisons for something a single O(n) pass
answers — mention it as the baseline, then discard it in the same breath.

If the tree were **not** a BST, the O(n²) scan collapses instead to: flatten,
sort, scan adjacent — O(n log n). The BST is what removes the sort.
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


def get_minimum_difference(root: TreeNode | None) -> int | None:
    stack: list[TreeNode] = []
    node = root
    previous: int | None = None  # not 0 — values may be negative
    best: int | None = None

    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        if previous is not None:
            gap = node.val - previous  # in-order is sorted, so never negative
            if best is None or gap < best:
                best = gap
        previous = node.val
        node = node.right

    return best  # None when there are fewer than two nodes


CASES = [
    (([4, 2, 6, 1, 3],), 1),
    (([10, 5, 20, None, 9, 11],), 1),  # closest pair is not parent and child
    (([1, 0, 48, None, None, 12, 49],), 1),
    (([236, 104, 701, None, 227, None, 911],), 9),
    (([0, -3, 9, -10, None, 5],), 3),  # negatives break a 0-seeded previous
    (([2, 1],), 1),
    (([1],), None),  # fewer than two nodes: no pair exists
    (([],), None),
]


def solve(values: list[int | None]) -> int | None:
    return get_minimum_difference(from_level_order(values))
