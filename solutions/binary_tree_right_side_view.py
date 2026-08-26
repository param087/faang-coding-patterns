"""Binary Tree Right Side View — LeetCode 199."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "right_side_view",
    "insight": "The answer is the last node of every level, not the right spine — a left subtree that runs deeper still shows through.",
    "time": "O(n)",
    "space": "O(w) for BFS, O(h) for the right-first DFS",
    "sections": [
        (
            "What it asks",
            """
Standing to the right of the tree, list the values you can see, top to bottom.
Precisely: **one value per depth — the rightmost node at that depth.**

Restating it as "one per depth" rather than "what you can see" is the move
here; it converts a visual description into something you can code, and it
immediately kills the wrong answer below.
""",
        ),
        (
            "The insight",
            """
Two clean implementations, both O(n):

**BFS.** Do the level-order loop and take `row[-1]` — or skip building the row
and append when `i == level_size - 1`. Obviously correct, and it is the version
to write if you already put level-order on the board.

**DFS, right child first.** Recurse carrying a depth. If `depth == len(view)`,
this is the first node you have reached at that depth, so record it. Because
you always descend right before left, "first reached at this depth" is exactly
"rightmost at this depth".

```python
if depth == len(view):
    view.append(node.val)
dfs(node.right, depth + 1)
dfs(node.left, depth + 1)
```

The DFS uses O(h) space instead of O(w), which matters on a wide tree — the
bottom level of a complete tree of 100 nodes holds ~50 of them in the queue.
The BFS is the safer answer on a 10⁴-node degenerate chain. Say which trade you
are making and the interviewer stops asking.
""",
        ),
        (
            "The wrong first answer: the right spine",
            """
Following `root.right` until it is null gives the right answer on every
symmetric example and fails the moment a left subtree runs deeper.

`[1,2,3,4]` — root 1, left child 2 with its own left child 4, right child 3.
The right spine is `[1, 3]`. The correct view is `[1, 3, 4]`: at depth 2 the
only node in the entire tree is 4, sitting in the left subtree, so it is
trivially the rightmost one and is visible.

Same trap in reverse: at a depth where the rightmost node exists, nothing in a
shallower left subtree can hide it. Depth is the only thing that decides
visibility — horizontal position never enters into it.
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


def right_side_view(root: TreeNode | None) -> list[int]:
    if not root:
        return []

    view: list[int] = []
    queue = deque([root])

    while queue:
        size = len(queue)
        for i in range(size):
            node = queue.popleft()
            if i == size - 1:  # last of this level = rightmost at this depth
                view.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return view


def right_side_view_dfs(root: TreeNode | None) -> list[int]:
    """Right child first: the first node reached at a depth is the visible one."""
    view: list[int] = []

    def walk(node: TreeNode | None, depth: int) -> None:
        if not node:
            return
        if depth == len(view):
            view.append(node.val)
        walk(node.right, depth + 1)
        walk(node.left, depth + 1)

    walk(root, 0)
    return view


CASES = [
    (([1, 2, 3, None, 5, None, 4],), [1, 3, 4]),
    (([1, 2, 3, 4],), [1, 3, 4]),  # not the right spine
    (([1, None, 3],), [1, 3]),
    (([],), []),
    (([1, 2],), [1, 2]),
    (([1, 2, 3, 4, 5, 6, 7],), [1, 3, 7]),
    (([-1, -2, None, -3],), [-1, -2, -3]),
]


def solve(values: list[int | None]) -> list[int]:
    return right_side_view(from_level_order(values))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args
        # The two implementations must agree, including on the spine trap.
        assert right_side_view_dfs(from_level_order(*args)) == expected, args
