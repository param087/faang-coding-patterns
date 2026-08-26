"""Vertical Order Traversal of a Binary Tree — LeetCode 987."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "vertical_traversal",
    "insight": "Tag every node with (column, row, value), sort once, then group — no traversal order gives you the value tiebreak for free.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Assign the root column 0; a left child is one column left, a right child one
column right, and every child is one row down. Report the values column by
column from leftmost to rightmost, each column top to bottom.

The clause that decides the problem: when two nodes share the **same row and
the same column**, they are ordered by **value**, ascending.

Ask for that rule explicitly if it is not stated. Its premium sibling,
LeetCode 314, breaks the same tie by traversal order instead, and the two
problems otherwise read identically.
""",
        ),
        (
            "The insight",
            """
The name says "traversal", which pushes people towards a BFS whose visit order
must somehow already be the answer. That is the trap: no traversal order
produces the value tiebreak for free.

So decouple the two halves.

> Collect `(column, row, value)` for every node in **any** order, sort the
> list once, then group by column.

Sorting tuples lexicographically gives exactly the specified priority — column,
then row, then value — in one line, and the traversal becomes an ordinary DFS
with no ordering obligations at all. Every bug about "which child do I enqueue
first" disappears, because the answer no longer depends on it.

O(n log n) rather than the O(n) a pure BFS would give, and that is the correct
trade: the value tiebreak is a sort by definition. If the interviewer pushes on
it, the honest refinement is a BFS by row (rows arrive in order, so no row key
is needed) with each column's per-row bucket sorted — still O(n log n) in the
worst case, when one row holds every node.
""",
        ),
        (
            "The tiebreak that decides it",
            """
`[1,2,3,4,6,5,7]` is the case that separates a correct solution from one that
passes the samples:

- Node 6 is the left child of 2 → row 2, column 0.
- Node 5 is the left child of 3 → row 2, column 0.

Same cell. BFS visits 6 first (its parent 2 came first), so a queue-order
solution emits column 0 as `[1, 6, 5]`. The required answer is `[1, 5, 6]` —
sorted by value.

Two more things that trip people up:

- **Columns can be negative,** so a dict keyed by column plus `sorted(keys)` at
  the end, or a min/max tracked during traversal. Indexing a list with a
  negative column silently wraps around and produces plausible garbage.
- **Duplicate values in one cell are kept, not deduplicated.** `[1,2,3,null,4,4]`
  has both 4s at row 2, column 0, and column 0 is `[1, 4, 4]`.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def vertical_traversal(root: TreeNode | None) -> list[list[int]]:
    tagged: list[tuple[int, int, int]] = []  # (column, row, value)

    def walk(node: TreeNode | None, row: int, col: int) -> None:
        if node is None:
            return
        tagged.append((col, row, node.val))
        walk(node.left, row + 1, col - 1)
        walk(node.right, row + 1, col + 1)

    walk(root, 0, 0)

    columns: dict[int, list[int]] = defaultdict(list)
    for col, _row, value in sorted(tagged):  # column, then row, then value
        columns[col].append(value)
    return [columns[col] for col in sorted(columns)]  # columns can be negative


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
    (([3, 9, 20, None, None, 15, 7],), [[9], [3, 15], [20], [7]]),
    (([1, 2, 3, 4, 5, 6, 7],), [[4], [2], [1, 5, 6], [3], [7]]),
    (([1, 2, 3, 4, 6, 5, 7],), [[4], [2], [1, 5, 6], [3], [7]]),  # the value tiebreak
    (([],), []),
    (([1],), [[1]]),
    (([1, 2, 3, None, 4, 4],), [[2], [1, 4, 4], [3]]),  # duplicates in one cell
    (([1, 2, None, 3, None, 4],), [[4], [3], [2], [1]]),  # left spine, negative columns
    (([0, -1, -2],), [[-1], [0], [-2]]),
]


def solve(values: list[int | None]) -> list[list[int]]:
    return vertical_traversal(from_level_order(values))
