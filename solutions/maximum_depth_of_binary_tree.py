"""Maximum Depth of Binary Tree — LeetCode 104."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "max_depth",
    "insight": "Depth is the rare tree quantity the parent wants verbatim: one plus the deeper child, so the recursion returns the answer itself.",
    "time": "O(n)",
    "space": "O(h) — O(n) on a degenerate chain",
    "sections": [
        (
            "What it asks",
            """
The number of **nodes** on the longest root-to-leaf path. A single node has
depth 1; the empty tree has depth 0.

Nodes, not edges — the opposite of Diameter of Binary Tree, which counts edges.
Confusing the two is an off-by-one on every case, so say which one you are
computing before you write a line.
""",
        ),
        (
            "The insight",
            """
Most tree problems make you separate *what the parent needs* from *what the
problem asks*. This one is the degenerate case where they are the same thing:

```
depth(node) = 1 + max(depth(left), depth(right))
```

The base case `depth(None) = 0` also handles leaves for free — a leaf gets
`1 + max(0, 0) = 1`. Writing a separate `if not node.left and not node.right`
branch is a sign you have not trusted the null case, and it is where the
one-child bugs live.

Post-order, one visit per node, O(n). Nothing beats that: you have to look at
every node to know none of them is deeper.
""",
        ),
        (
            "The recursion limit is a real constraint",
            """
LeetCode allows 10⁴ nodes and does **not** promise the tree is balanced. A
degenerate left chain of 10⁴ nodes recurses 10⁴ frames deep, and CPython's
default limit is **1000** — the recursive answer raises `RecursionError` on
input the problem explicitly permits.

Interviewers rarely push this, but if yours does, do not reach for
`sys.setrecursionlimit`; that just trades a clean exception for a segfault.
Iterate instead — a BFS keeping a level count, or an explicit stack of
`(node, depth)` pairs:

```python
stack = [(root, 1)]
while stack:
    node, d = stack.pop()
    best = max(best, d)
    ...
```

`check()` below builds a 2000-deep chain precisely to make this concrete.
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


def max_depth(root: TreeNode | None) -> int:
    if not root:
        return 0
    # A leaf falls out of this for free: 1 + max(0, 0).
    return 1 + max(max_depth(root.left), max_depth(root.right))


def max_depth_iterative(root: TreeNode | None) -> int:
    """BFS by levels — the version that survives a 10⁴-node chain."""
    if not root:
        return 0
    depth = 0
    queue = deque([root])
    while queue:
        depth += 1
        for _ in range(len(queue)):  # exactly one level
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return depth


CASES = [
    (([3, 9, 20, None, None, 15, 7],), 3),
    (([1, None, 2],), 2),
    (([1],), 1),
    (([],), 0),
    (([1, 2, 3, 4, None, None, 5, 6],), 4),
    (([-1, -2, -3],), 2),
]


def solve(values: list[int | None]) -> int:
    return max_depth(from_level_order(values))


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args
        assert max_depth_iterative(from_level_order(*args)) == expected, args

    # 2000 deep, i.e. past CPython's default recursion limit of 1000. The
    # iterative version is the only one that answers.
    chain = from_level_order([1] + [1, None] * 1999)
    assert max_depth_iterative(chain) == 2000
