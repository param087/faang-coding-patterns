"""Path Sum — LeetCode 112."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "has_path_sum",
    "insight": "Subtract as you descend and test the remainder at a leaf — and a null pointer is not a leaf, which is the whole bug surface.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Is there a **root-to-leaf** path whose values sum to `targetSum`? A leaf is a
node with no children at all — not a node with one child, and not a null
pointer.

Two things to confirm out loud: values can be **negative** (−1000 to 1000 on
LeetCode), and the empty tree is `False` even when the target is 0, because
there is no path.
""",
        ),
        (
            "The insight",
            """
Carry the remaining target down instead of accumulating a running sum upward:

```
has(node, remaining) → has(child, remaining - node.val)
```

Then the leaf test is `remaining == node.val` — one comparison, no separate
accumulator, and the recursion needs no extra state. Either direction works;
subtracting reads better and makes the leaf condition a single equality.

The structure is `or`, not `and`: **any** qualifying path is enough, so
short-circuit on the left subtree and never touch the right if it hits.
""",
        ),
        (
            "The pitfall: `if not node` is the wrong base case",
            """
Writing the base case as

```python
if not node:
    return remaining == 0     # WRONG
```

looks equivalent and is not. Take the tree `[1,2]` with `targetSum = 1`. The
root has value 1 and a **null right child**; that null child sees
`remaining == 0` and reports success. But the only root-to-leaf path is
1 → 2 = 3, so the answer is `False`.

The rule: a null pointer means "there is no subtree here", never "the path ends
here". Test for a leaf explicitly —
`if not node.left and not node.right: return remaining == node.val` — and
return `False` for null.

The second trap is pruning. On non-negative values you can stop descending once
the running sum exceeds the target; with negatives in range that optimisation
is simply wrong, and it is exactly the sort of thing an interviewer plants by
mentioning "all values are positive" and then quietly removing the constraint.
`[1,-2,-3,1,3,-2,null,-1]` with target −1 is `True` via 1 → −2 → 1 → −1, and
that path dips below the target before recovering.
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


def has_path_sum(root: TreeNode | None, target_sum: int) -> bool:
    if not root:
        return False  # not a path end — there is simply no node here
    if not root.left and not root.right:  # the only real terminal
        return target_sum == root.val
    remaining = target_sum - root.val
    return has_path_sum(root.left, remaining) or has_path_sum(root.right, remaining)


CASES = [
    (([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], 22), True),
    (([1, 2, 3], 5), False),
    (([1, 2, 3], 4), True),
    (([1, 2], 1), False),  # the null-is-not-a-leaf case
    (([], 0), False),
    (([1], 1), True),
    (([1, -2, -3, 1, 3, -2, None, -1], -1), True),
    (([1, -2, -3, 1, 3, -2, None, -1], 0), False),
]


def solve(values: list[int | None], target_sum: int) -> bool:
    return has_path_sum(from_level_order(values), target_sum)
