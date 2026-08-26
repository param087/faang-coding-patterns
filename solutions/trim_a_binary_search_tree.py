"""Trim a Binary Search Tree — LeetCode 669."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "trim_bst",
    "insight": "An out-of-range node is not deleted — it is replaced by the trimmed subtree on the side that can still hold valid values.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Remove every node outside `[low, high]` from a BST and return the new root.
Every remaining node must keep its original descendant relationships — you are
not allowed to collect the surviving values and rebuild a fresh (say, balanced)
tree, even though that would also be a BST containing exactly those values.

Ask: are the bounds inclusive (yes); is the tree guaranteed to have a node left
(no — the answer can be empty); can I mutate the input tree in place (normally
yes, and that is what makes the one-line recursion possible).
""",
        ),
        (
            "The insight",
            """
Three cases per node, and the ordering makes two of them free:

- `node.val < low` → the node *and its entire left subtree* are too small.
  Everything that can survive is in the right subtree, so the answer for this
  position is `trim(node.right)`.
- `node.val > high` → mirror: return `trim(node.left)`.
- otherwise the node survives; trim both children and reattach.

That last reattachment is what preserves structure: a surviving node keeps the
same subtrees, just shorter ones. Nothing is ever moved sideways.

The recursion returns **the replacement for this position**, not a boolean and
not `None`. Once you see the return value that way, the function is five lines
and the correctness argument is one sentence per case.
""",
        ),
        (
            "Why you return the recursion, not None",
            """
The wrong first answer is:

```python
if node.val < low:
    return None
```

It looks right — the node is out of range, so drop it. But dropping the node
also drops its **right** subtree, which may be full of in-range values.

Concretely: tree `3 → left 0 → right 2 → left 1`, trimming to `[1, 3]`. Node
`0` is below `low`. Returning `None` there deletes `2` and `1` with it and you
answer `[3]` instead of `[3, 2, null, 1]`.

The rule to say out loud: **an out-of-range node is replaced, not removed.**
Its subtree on the still-viable side is promoted into its slot.

One follow-up worth pre-empting: trimming to a range with `low > high` is not
in the constraints, but the same code returns an empty tree for it, which is
the only sensible answer.
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


def to_level_order(root: TreeNode | None) -> list[int | None]:
    if root is None:
        return []
    out: list[int | None] = []
    queue: deque[TreeNode | None] = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def trim_bst(root: TreeNode | None, low: int, high: int) -> TreeNode | None:
    if root is None:
        return None
    if root.val < low:
        # The node and its left subtree are all too small; promote the right side.
        return trim_bst(root.right, low, high)
    if root.val > high:
        return trim_bst(root.left, low, high)
    # Survivor: keep the node, shorten its subtrees in place.
    root.left = trim_bst(root.left, low, high)
    root.right = trim_bst(root.right, low, high)
    return root


CASES = [
    (([1, 0, 2], 1, 2), [1, None, 2]),
    (([3, 0, 4, None, 2, None, None, 1], 1, 3), [3, 2, None, 1]),  # promotion, not deletion
    (([10, 5, 15, 3, 7, 13, 18, 1, 4, 6, 8], 6, 14), [10, 7, 13, 6, 8]),
    (([2, 1, 3], 3, 4), [3]),  # root itself is trimmed away
    (([1], 1, 1), [1]),
    (([1], 2, 3), []),  # nothing survives
    (([0, -5, 5, -8, -2, 2, 8], -4, 3), [0, -2, 2]),  # negatives
    (([], 1, 2), []),
]


def solve(values: list[int | None], low: int, high: int) -> list[int | None]:
    # trim_bst rewrites child pointers, so build a fresh tree per call.
    return to_level_order(trim_bst(from_level_order(values), low, high))
