"""Convert Sorted Array to Binary Search Tree — LeetCode 108."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "sorted_array_to_bst",
    "insight": "The array is already the in-order traversal, so picking the middle element as the root makes balance automatic.",
    "time": "O(n)",
    "space": "O(log n) for the recursion",
    "sections": [
        (
            "What it asks",
            """
Build a **height-balanced** BST from a sorted array. Any valid answer is
accepted, so there is no single expected tree — which is worth confirming,
because otherwise you would be reverse-engineering a specific shape.

"Height-balanced" here means the depths of the two subtrees of every node
differ by at most one. Ask whether duplicates can appear (LeetCode: yes, values
are non-decreasing) — they are harmless for construction, but they do mean a
subsequent `search` may find any one of them.
""",
        ),
        (
            "The insight",
            """
Read the input for what it is: **the in-order traversal of the tree you are
being asked to produce**. You are inverting a traversal, not sorting anything.

That fixes the recursion immediately. Whatever element you choose as the root,
everything to its left in the array must form the left subtree and everything
to its right the right subtree — the BST property is satisfied by construction
for *any* choice of pivot. The only freedom left is which element to pick, and
that is where balance comes from.

Pick the **middle**. Then each side has at most one more element than the
other, so the two subtree heights differ by at most one, at every level,
recursively. Balance is not something you fix afterwards; it falls out of the
pivot choice.

Pick the first element instead and you get a right-leaning chain of n nodes —
still a valid BST, but height n, and the point of the exercise is gone.

Recurse on index bounds, not on slices. `nums[:mid]` copies, turning an O(n)
build into O(n log n) time and O(n log n) allocation. Interviewers notice.
""",
        ),
        (
            "Edge cases",
            """
- **Empty array** — return `None`. The `lo > hi` base case covers it with no
  special-casing, which is why bounds beat slices twice over.
- **One element** — `lo == hi`, both recursive calls hit the base case.
- **Even length** — `(lo + hi) // 2` takes the lower middle; `(lo + hi + 1) //
  2` takes the upper. Both are balanced, both are accepted, and they produce
  different trees. Say which you picked so nobody thinks you tripped over it.
- **Duplicates** — `[1, 1, 1]` builds fine; the equal values land on whichever
  side the split puts them, which is why "is this a strict BST?" matters for
  any later `search`.
- **Negatives** — irrelevant to the algorithm; the ordering is all that is
  used, never the magnitude.
- **Very large n** — recursion depth is O(log n), about 17 for 10⁵ elements, so
  the stack is safe here even though it is not for skewed-tree problems.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


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


def sorted_array_to_bst(nums: list[int]) -> TreeNode | None:
    def build(lo: int, hi: int) -> TreeNode | None:
        if lo > hi:
            return None
        mid = (lo + hi) // 2  # lower middle; the upper middle is equally valid
        # Indices, not slices: slicing would make this O(n log n).
        return TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi))

    return build(0, len(nums) - 1)


CASES = [
    (([-10, -3, 0, 5, 9],), [0, -10, 5, None, -3, None, 9]),
    (([1, 2, 3, 4, 5, 6, 7],), [4, 2, 6, 1, 3, 5, 7]),  # perfect tree
    (([1, 2, 3, 4, 5, 6],), [3, 1, 5, None, 2, 4, 6]),  # even length
    (([1, 3],), [1, None, 3]),
    (([-5, -4, -3, -2],), [-4, -5, -3, None, None, None, -2]),
    (([7],), [7]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int | None]:
    return to_level_order(sorted_array_to_bst(nums))
