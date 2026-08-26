"""Path Sum III — LeetCode 437."""

from __future__ import annotations

from collections import defaultdict, deque

META = {
    "pattern": "prefix-sums",
    "insight": "The root-to-node path is an array; carry a prefix-sum count map down it and every downward path is a subarray-sum-equals-k hit.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Count the paths whose values sum to `targetSum`. Paths must go **downwards**
— parent to child — but need not start at the root or end at a leaf.

Two things to confirm before writing anything: values may be **negative** (they
can, which forbids any early cut-off), and the running sum can exceed 32 bits
on a 1000-node tree, which is why the LeetCode signature is `long` in Java.
Python does not care; say it anyway.
""",
        ),
        (
            "The insight",
            """
The obvious answer is a double recursion: for every node, walk every downward
path starting there. `O(n·h)` — `O(n²)` on a skewed tree, so 10⁶ node visits at
`n = 1000`. It passes, and it is the answer that stops the follow-up
conversation.

The linear answer: **at any moment during a DFS, the stack of ancestors is an
array**, and a downward path ending at the current node is a contiguous
subarray of it. So this is Subarray Sum Equals K with a tree-shaped input.

Carry `running` = sum from the root to the current node, and a map from prefix
value to how many ancestors produced it. At each node, `seen[running - target]`
is the number of ancestors `a` such that the path from `a`'s child down to here
sums to `target`. Seed with `{0: 1}` for the empty prefix, which is what makes
paths starting at the root count.

One visit per node, `O(n)`; the map holds one entry per ancestor, `O(h)`.
""",
        ),
        (
            "The un-do is the whole trick",
            """
After recursing into both children you **must** decrement `seen[running]` on
the way back up. The map is meant to describe the current root-to-node path
only; leave a sibling's prefixes in it and you count paths that bend sideways,
which is not a path at all.

`[1, 4, 3]` with `targetSum = -1` is the smallest test that exposes it. The
correct answer is **0** — every value is positive. Without the decrement, the
right child sees `running = 4`, looks for `4 - (-1) = 5`, and finds the prefix
`1 + 4 = 5` left behind by the left child. It returns 1.

Note that this is why a defaultdict read is safe but a `del` is not: entries
can legitimately fall to zero and come back. Decrement; do not remove.

Also: recursion depth is `h`, and a degenerate 1000-node chain sits right on
CPython's default limit. On a real judge that is fine; if an interviewer asks
about a million-node tree, convert to an explicit stack carrying `(node,
running)` plus an un-do marker.
""",
        ),
    ],
}


class TreeNode:
    __slots__ = ("left", "right", "val")

    def __init__(self, val: int = 0) -> None:
        self.val = val
        self.left: TreeNode | None = None
        self.right: TreeNode | None = None


def from_level_order(values: list[int | None]) -> TreeNode | None:
    """LeetCode's level-order format: `None` marks a missing child."""
    if not values or values[0] is None:
        return None

    root = TreeNode(values[0])
    queue = deque([root])
    index = 1

    while queue and index < len(values):
        node = queue.popleft()
        for side in ("left", "right"):
            if index >= len(values):
                break
            value = values[index]
            index += 1
            if value is not None:
                child = TreeNode(value)
                setattr(node, side, child)
                queue.append(child)

    return root


def path_sum(root: TreeNode | None, target_sum: int) -> int:
    seen: defaultdict[int, int] = defaultdict(int)
    seen[0] = 1  # the empty prefix: paths that start at the root

    def walk(node: TreeNode | None, running: int) -> int:
        if node is None:
            return 0

        running += node.val
        count = seen[running - target_sum]  # ancestors that close a valid path

        seen[running] += 1
        count += walk(node.left, running) + walk(node.right, running)
        seen[running] -= 1  # un-do: this prefix is not on a sibling's path

        return count

    return walk(root, 0)


CASES = [
    (([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1], 8), 3),
    (([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22), 3),
    (([1, 4, 3], -1), 0),
    (([0, 1, 1], 1), 4),
    (([1, None, 2, None, 3, None, 4, None, 5], 3), 2),
    (([-1, -2, -3], -3), 2),
    (([], 0), 0),
]


def solve(values: list[int | None], target_sum: int) -> int:
    return path_sum(from_level_order(values), target_sum)
