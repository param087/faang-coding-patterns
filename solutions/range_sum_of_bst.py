"""Range Sum of BST — LeetCode 938."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "range_sum_bst",
    "insight": "Drop a whole subtree the moment the ordering proves every value in it falls outside [low, high].",
    "time": "O(h + k) with pruning, where k is the number of in-range nodes",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Sum the values of every node in a BST whose value lies in `[low, high]`.
Both bounds are **inclusive** — confirm that out loud, because an exclusive
reading changes the answer on every test case that touches a boundary.

Worth asking: can values be negative (yes — which kills any "stop once the sum
stops growing" idea), and is the tree balanced (it is not guaranteed, so the
recursion depth is a real concern at n = 2·10⁴).
""",
        ),
        (
            "The insight",
            """
Any traversal that visits all n nodes and adds the ones in range is correct.
It is also the answer that ends the question badly, because it never uses the
word "search" in "binary search tree".

At each node there are three cases, and two of them throw away half the work:

- `node.val < low` → every value in the **left** subtree is smaller still, so
  the entire left subtree is out of range. Recurse right only.
- `node.val > high` → symmetric. Recurse left only.
- otherwise the node counts, and both children may contain in-range values.

The recursion visits only nodes on the two boundary search paths plus the
nodes actually inside the range: **O(h + k)**. On a 2·10⁴-node tree with three
values in range, that is roughly 30 visits instead of 20,000.
""",
        ),
        (
            "The pruning is the whole question",
            """
This is an Easy that is graded as a Medium. Two things decide it:

1. **The pruned branches must be `return`, not fall-through.** Writing
   `if node.val >= low: go left` *and* `if node.val <= high: go right` as two
   independent guards is correct too — but only if you also guard the addition
   with `low <= node.val <= high`. Mixing the two styles is where the
   off-by-one lands.
2. **State the complexity as O(h + k), not O(n).** Saying O(n) after writing
   the pruned version suggests you did not know why you wrote it.

If they push on recursion depth — a strictly increasing insertion order gives
a 2·10⁴-deep chain, well past CPython's default 1000-frame limit — switch to
the explicit stack version, which is the same three cases with a `while`.
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


def range_sum_bst(root: TreeNode | None, low: int, high: int) -> int:
    if root is None:
        return 0
    if root.val < low:
        return range_sum_bst(root.right, low, high)  # whole left subtree is too small
    if root.val > high:
        return range_sum_bst(root.left, low, high)  # whole right subtree is too large
    return root.val + range_sum_bst(root.left, low, high) + range_sum_bst(root.right, low, high)


def range_sum_iterative(root: TreeNode | None, low: int, high: int) -> int:
    """Same three cases, an explicit stack — use this if depth is a concern."""
    total = 0
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if node.val < low:
            stack.append(node.right)
        elif node.val > high:
            stack.append(node.left)
        else:
            total += node.val
            stack.append(node.left)
            stack.append(node.right)
    return total


CASES = [
    (([10, 5, 15, 3, 7, None, 18], 7, 15), 32),
    (([10, 5, 15, 3, 7, 13, 18, 1, None, 6], 6, 10), 23),
    (([10, 5, 15, 3, 7, None, 18], 1, 100), 58),  # everything in range
    (([10, 5, 15], 20, 30), 0),  # range entirely above the tree
    (([0, -5, 5, -8, -2, 2, 8], -5, 2), -5),  # negatives, and a negative total
    (([1], 1, 1), 1),  # single node, degenerate range
    (([1], 2, 3), 0),
    (([], 1, 10), 0),
]


def solve(values: list[int | None], low: int, high: int) -> int:
    root = from_level_order(values)
    recursive = range_sum_bst(root, low, high)
    assert recursive == range_sum_iterative(root, low, high)
    return recursive
