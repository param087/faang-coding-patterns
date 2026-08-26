"""Binary Tree Level Order Traversal — LeetCode 102."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "level_order",
    "insight": "Snapshot the queue length before draining it — that count is exactly one level, and it is all that separates BFS from level-aware BFS.",
    "time": "O(n)",
    "space": "O(w) — the widest level, up to n/2",
    "sections": [
        (
            "What it asks",
            """
Return the node values level by level, top to bottom and left to right within
each level — a list of lists, not one flat list. Empty tree gives `[]`.

This is the template problem for a whole family: zigzag order, bottom-up order,
level averages, largest value per row, right-side view. Write it once, cleanly,
and those are all one-line edits.
""",
        ),
        (
            "The insight",
            """
A plain BFS visits the nodes in the right order but loses the level boundaries.
You need one extra fact per iteration, and the cheapest source of it is the
queue itself:

```python
for _ in range(len(queue)):   # frozen before the loop body appends
```

At the top of the outer loop the queue holds **exactly** the current level, so
`len(queue)` is that level's width. Capture it, pop that many, and every node
you append lands in the next level.

Two things go wrong if you skip the snapshot:

- `while queue:` with no inner count flattens everything into one list.
- `for node in queue:` mutates a deque while iterating it — Python raises
  `RuntimeError`, and the equivalent in a language that does not will loop
  forever.

The DFS alternative is worth naming: recurse carrying a `depth`, and append to
`result[depth]`, creating the row when `depth == len(result)`. Same O(n),
pre-order guarantees left-to-right within a row, and it is the version that
makes right-side view trivial.
""",
        ),
        (
            "Follow-ups",
            """
- **Zigzag (LC 103)** — reverse alternate rows *after* building them, or
  `appendleft` into a deque. Do not reverse the queue itself; you will corrupt
  the parent order for the level below.
- **Bottom-up (LC 107)** — build normally, then reverse the outer list. O(n),
  and cleaner than trying to BFS upwards.
- **Right-side view (LC 199)** — take `row[-1]`.
- **Level averages, level maxima, level sums** — all the same loop body.
- **Vertical order (LC 987)** — no longer a pure BFS: you have to carry a
  column index and sort ties by row then value.
- **N-ary tree** — replace the two `if node.left / node.right` lines with a
  loop over `node.children`. Nothing else changes.
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


def level_order(root: TreeNode | None) -> list[list[int]]:
    if not root:
        return []

    levels: list[list[int]] = []
    queue = deque([root])

    while queue:
        row: list[int] = []
        for _ in range(len(queue)):  # frozen: exactly this level
            node = queue.popleft()
            row.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(row)

    return levels


CASES = [
    (([3, 9, 20, None, None, 15, 7],), [[3], [9, 20], [15, 7]]),
    (([1],), [[1]]),
    (([],), []),
    (([1, 2, 3, 4, None, None, 5],), [[1], [2, 3], [4, 5]]),
    (([1, None, 2, None, 3],), [[1], [2], [3]]),
    (([-1, -2, -3, -4],), [[-1], [-2, -3], [-4]]),
    (([1, 1, 1, 1, 1],), [[1], [1, 1], [1, 1]]),
]


def solve(values: list[int | None]) -> list[list[int]]:
    return level_order(from_level_order(values))
