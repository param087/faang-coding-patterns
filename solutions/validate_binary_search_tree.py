"""Validate Binary Search Tree — LeetCode 98."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "is_valid_bst",
    "insight": "BST-ness is a global property, so carry the allowed range down rather than checking each node against its children.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Decide whether a binary tree satisfies the BST property: every node in the
left subtree is smaller, every node in the right subtree is larger.

Ask: are duplicates allowed, and if so which side; is a single node valid
(yes); an empty tree (yes); are values bounded enough that infinities work as
sentinels.
""",
        ),
        (
            "The trap — volunteer it",
            """
Almost everyone falls into this once, so say it before the interviewer does:

> "The obvious check is that each node sits between its children — but that's
> **local**, and BST-ness is **global**."

Then draw the counterexample:

```
      5
     / \\
    1   4
       / \\
      3   6
```

Every parent-child relationship is individually fine. But 3 is in 5's *right*
subtree and smaller than 5, so this is not a BST. A local check cannot see
that relationship.
""",
        ),
        (
            "The insight",
            """
Pass down the **open interval** each subtree is allowed to occupy. Going left
tightens the upper bound to the current value; going right tightens the lower
bound.

The constraint accumulates as you descend, which is exactly what makes it a
global check.

In the counterexample, node 4's right child must lie in `(4, 5)` — so 6 fails
immediately.
""",
        ),
        (
            "The other solution",
            """
Do an in-order traversal and confirm it is **strictly increasing**. Equally
correct, and sometimes easier to explain, because it leans on the one fact
that carries the whole BST category: the in-order traversal of a BST is
sorted.

Have both. The traversal version also generalises straight into the iterative
answer if they ask for one.
""",
        ),
        (
            "The bounds must be exclusive",
            """
`low < node.val < high`, not `<=`. With `<=`, equal values pass validation,
which is wrong unless the problem explicitly allows duplicates on one side.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it iteratively"** — the in-order traversal with an explicit stack and
  a `previous` variable checking strict increase.
- **Recover Binary Search Tree** — exactly two nodes were swapped; find them
  by spotting the two descents in the in-order sequence.
- **Largest BST Subtree** — return `(is_bst, min, max, size)` from each node,
  which is the same "return more than the answer" idea as
  [diameter](../../patterns/binary-trees/).
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


def is_valid_bst(root: TreeNode | None) -> bool:
    def valid(node: TreeNode | None, low: float, high: float) -> bool:
        if not node:
            return True
        # Exclusive bounds: equal values are not valid on either side.
        if not low < node.val < high:
            return False
        # Descending tightens the range — this is what makes it global.
        return valid(node.left, low, node.val) and valid(node.right, node.val, high)

    return valid(root, float("-inf"), float("inf"))


CASES = [
    (([2, 1, 3],), True),
    (([5, 1, 4, None, None, 3, 6],), False),
    (([5, 1, 4, None, None, 3, 7],), False),  # the local-check counterexample
    (([1],), True),
    (([],), True),
    (([2, 2, 2],), False),  # duplicates are not valid
    (([10, 5, 15, None, None, 6, 20],), False),  # 6 is in 10's right subtree
]


def solve(values: list[int | None]) -> bool:
    return is_valid_bst(from_level_order(values))
