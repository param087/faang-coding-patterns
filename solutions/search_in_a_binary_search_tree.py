"""Search in a Binary Search Tree — LeetCode 700."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "search_bst",
    "insight": "Every comparison discards an entire subtree, so this is binary search with pointers instead of indices.",
    "time": "O(h) — O(log n) balanced, O(n) on a degenerate chain",
    "space": "O(1) iterative",
    "sections": [
        (
            "What it asks",
            """
Given the root of a BST and a target value, return the **subtree rooted at the
matching node**, or nothing if no node holds that value.

Returning a subtree rather than a boolean is the only wrinkle: you hand back
the node itself, so the caller keeps its children.

Worth asking: can values repeat? A textbook BST says no, and LeetCode
guarantees it here — if duplicates were allowed you would have to define which
side they live on before the descent is even well defined.
""",
        ),
        (
            "The insight",
            """
Each comparison eliminates a whole subtree. `target < node.val` means every
node to the right is also too large, so the right half of the remaining tree
disappears in one step. That is binary search, expressed with pointers rather
than array indices.

The cost is therefore the **height**, not the node count: O(log n) if the tree
is balanced, O(n) if it has degenerated into a linked list. Say "O(h)" and then
give both bounds — the interviewer is checking that you know the tree is not
balanced by assumption.

Write it iteratively. The recursion here is pure tail recursion, CPython does
not eliminate it, and a 10⁵-node skewed tree will blow the default recursion
limit of 1000. The `while` loop is the same three lines with O(1) space.
""",
        ),
        (
            "Edge cases",
            """
- **Empty tree** — the loop simply never runs and returns `None`. No special
  case needed, which is the point of writing it as a `while node` loop.
- **Value absent** — you fall off the bottom and return `None`. Do not return
  the last node you touched; that is the "closest value" problem
  (LeetCode 270), a different question.
- **Match at the root** — the loop exits on the first iteration.
- **Negative values** — nothing breaks; the comparison is ordinary integer
  ordering, so do not reach for `abs` or sentinels.
- **Duplicates, if they were allowed** — the first match wins and you must
  agree with the interviewer whether that is the one they want.
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
    """Serialise back to LeetCode's level-order list, trailing nulls trimmed."""
    if not root:
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


def search_bst(root: TreeNode | None, val: int) -> TreeNode | None:
    node = root
    while node and node.val != val:
        # One comparison, one subtree gone.
        node = node.left if val < node.val else node.right
    return node  # the matching subtree, or None if we fell off the bottom


CASES = [
    (([4, 2, 7, 1, 3], 2), [2, 1, 3]),  # returns the subtree, not just True
    (([4, 2, 7, 1, 3], 5), []),  # absent — not the nearest node
    (([4, 2, 7, 1, 3], 4), [4, 2, 7, 1, 3]),  # match at the root
    (([4, 2, 7, 1, 3], 7), [7]),
    (([], 1), []),
    (([1], 1), [1]),
    (([0, -3, 9, -10, None, 5], -3), [-3, -10]),  # negatives
]


def solve(values: list[int | None], val: int) -> list[int | None]:
    return to_level_order(search_bst(from_level_order(values), val))
