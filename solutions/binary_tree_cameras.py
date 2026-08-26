"""Binary Tree Cameras — LeetCode 968."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "dp-advanced",
    "insight": "A node has exactly three useful conditions — has a camera, covered by a child, not yet covered — and the parent picks.",
    "time": "O(n)",
    "space": "O(h) recursion",
    "sections": [
        (
            "What it asks",
            """
A camera placed on a node monitors that node, its parent and its immediate
children. Find the minimum number of cameras that monitors every node.

Clarify the range: a camera covers **distance 1 only**, not the whole subtree.
People who mis-hear this write a completely different (and much easier) problem.
""",
        ),
        (
            "The insight",
            """
The wrong first answer is "put cameras on every second level" or "put cameras
on all parents of leaves and dedupe". Both are close, and both are wrong on
skewed trees, because the decision at a node depends on information the node
does not have — whether its **parent** intends to cover it.

So push that choice up. Each node reports the cost of three conditions:

- **`WITH`** — a camera sits here.
- **`COVERED`** — no camera here, but some child has one.
- **`OPEN`** — no camera here and no child has one, so the parent *must* place
  one. This is a promise to the parent, not a valid final state.

The recurrences fall straight out:

```
WITH    = 1 + min(all three of left) + min(all three of right)
COVERED = min( L.WITH + min(R.WITH, R.COVERED),
               R.WITH + min(L.WITH, L.COVERED) )
OPEN    = L.COVERED + R.COVERED
```

`WITH` takes `min` over all three child states because a camera here covers the
children whatever they chose. `COVERED` insists that **at least one** child
actually has a camera — that `min` of two symmetric terms is where sloppy
versions go wrong, quietly allowing "covered by nobody".

For a missing child return `(∞, 0, 0)`: a null can never hold a camera, and it
needs no coverage, so it costs nothing in either passive state.

The answer is `min(root.WITH, root.COVERED)` — the root has no parent, so
leaving it `OPEN` is not allowed.
""",
        ),
        (
            "Sanity checks and the greedy alternative",
            """
- **A leaf** evaluates to `(1, ∞, 0)`. `COVERED` is infinite because a leaf has
  no children to cover it. If your leaf comes out with a finite `COVERED`, the
  "at least one child has a camera" condition is broken.
- **A single node** answers 1, not 0 — a bare root still needs monitoring.
- **A three-node chain** answers 1: the camera goes on the middle node, not on
  the root. Any "start at the root" heuristic gets 2 here.
- **The greedy** — post-order, place a camera the moment a child reports itself
  uncovered — gets the same answer in O(n) with less code, and is worth
  mentioning. The three-state DP is what you write when the follow-up changes
  ("cameras cost different amounts per node", "radius 2"), because greedy stops
  generalising and the DP just gains states.
- **Depth**: a 10⁴-node left chain will blow CPython's default recursion limit.
  Say so, and offer the explicit-stack post-order if pressed.
""",
        ),
    ],
}

INF = 10**9


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


def min_camera_cover(root: TreeNode | None) -> int:
    def solve_node(node: TreeNode | None) -> tuple[int, int, int]:
        """(camera here, covered by a child, not covered — parent must act)."""
        if node is None:
            return (INF, 0, 0)  # a null holds no camera and needs no cover

        left = solve_node(node.left)
        right = solve_node(node.right)

        with_camera = 1 + min(left) + min(right)
        covered = min(
            left[0] + min(right[0], right[1]),  # left has the camera
            right[0] + min(left[0], left[1]),  # right has the camera
        )
        open_node = left[1] + right[1]  # both children covered, neither armed

        return (with_camera, covered, open_node)

    with_camera, covered, _ = solve_node(root)
    return min(with_camera, covered)  # the root has no parent to rescue it


CASES = [
    (([0, 0, None, 0, None],), 1),
    (([0, 0, None, 0, 0],), 1),
    (([0],), 1),
    (([],), 0),
    (([0, 0],), 1),
    (([0, 0, 0, 0, 0, 0, 0],), 2),
    (([0, 0, None, None, 0, 0, None, None, 0, 0],), 2),
    (([0, None, 0, None, 0, None, 0],), 2),
]


def solve(values: list[int | None]) -> int:
    return min_camera_cover(from_level_order(list(values)))
