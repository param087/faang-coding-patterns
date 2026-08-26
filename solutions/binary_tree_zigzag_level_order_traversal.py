"""Binary Tree Zigzag Level Order Traversal — LeetCode 103."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "zigzag_level_order",
    "insight": "Run an ordinary left-to-right BFS and flip the row as you build it; flipping the queue instead scrambles every level below.",
    "time": "O(n)",
    "space": "O(w) for the queue, where w is the widest level",
    "sections": [
        (
            "What it asks",
            """
Level-order traversal, but alternate rows read right to left: level 0 forward,
level 1 reversed, level 2 forward, and so on.

Confirm the direction of level 0 — it is **left to right**, so the first flip
happens at level 1. Getting that backwards inverts every row and the diff looks
mystifying.
""",
        ),
        (
            "The insight",
            """
The traversal does not change. Only the **presentation of each row** changes.

Keep the standard level-order skeleton — snapshot `len(queue)` so you know
where the level ends, always enqueue `left` then `right` — and build the row
into a `deque`, using `appendleft` on reversed levels. That is O(1) per node,
so no reversal pass and no `list.insert(0, ...)`, which would be O(k) per node
and turn a wide level into quadratic work.

`row.reverse()` at the end of the level is equally fine and one character
shorter to reason about. The point is that the flip lives in the **row**, never
in the queue.

A DFS carrying a depth works too: append to `levels[depth]`, then reverse the
odd-indexed lists at the end. Worth mentioning if asked for a recursive
version, but BFS is the natural fit when the output is grouped by level.
""",
        ),
        (
            "The wrong first answer",
            """
The tempting move is to alternate the **enqueue order** — push right child
before left on flipped levels and read the queue normally. It survives a trace
of the first two levels, then falls apart on the third.

Take `[1,2,3,4,5,6,7]`:

- Level 0: pop 1, enqueue right(3) then left(2). Queue `[3, 2]`.
- Level 1 prints `[3, 2]`. Correct.
- Level 2: pop 3 → enqueue 6, 7; pop 2 → enqueue 4, 5. Queue `[6, 7, 4, 5]`.
- Level 2 prints `[6, 7, 4, 5]`, but the answer is `[4, 5, 6, 7]`.

A FIFO queue only reverses **once**; the parents were already in flipped order,
so their children come out flipped by parent and forward within each parent.
The classic **two-stack** version does work, because a stack reverses again on
the way out — but it is more moving parts than one `deque` per row.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def zigzag_level_order(root: TreeNode | None) -> list[list[int]]:
    if root is None:
        return []

    levels: list[list[int]] = []
    queue = deque([root])
    left_to_right = True

    while queue:
        row: deque[int] = deque()
        for _ in range(len(queue)):  # snapshot: the level ends here
            node = queue.popleft()
            if left_to_right:
                row.append(node.val)
            else:
                row.appendleft(node.val)  # the flip lives in the row, not the queue
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        levels.append(list(row))
        left_to_right = not left_to_right

    return levels


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
    (([3, 9, 20, None, None, 15, 7],), [[3], [20, 9], [15, 7]]),
    (([1, 2, 3, 4, 5, 6, 7],), [[1], [3, 2], [4, 5, 6, 7]]),  # breaks the flipped queue
    (([1],), [[1]]),
    (([],), []),
    (([1, 2, None, 3, None, 4],), [[1], [2], [3], [4]]),  # left spine
    (([1, None, 2, None, 3],), [[1], [2], [3]]),  # right spine
    (([0, -1, -2, None, -3],), [[0], [-2, -1], [-3]]),
]


def solve(values: list[int | None]) -> list[list[int]]:
    return zigzag_level_order(from_level_order(values))
