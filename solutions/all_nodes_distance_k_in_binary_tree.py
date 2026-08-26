"""All Nodes Distance K in Binary Tree — LeetCode 863."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "distance_k",
    "insight": "Distance is a graph notion, not a tree notion — add parent pointers and the answer is one plain BFS from the target.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given a binary tree, a target **node** and an integer `k`, return the values of
every node exactly `k` edges away — upward through ancestors as well as
downward.

Two things worth pinning down:

- **Is the target given as a node reference or a value?** LeetCode hands you the
  node. If it is a value, you need uniqueness (LeetCode guarantees it) and one
  extra scan to find it. This module takes a value, so it does that scan.
- **Does the output order matter?** No — any order is accepted, which is a hint
  that the intended solution is a BFS frontier rather than an ordered walk.
""",
        ),
        (
            "The insight",
            """
The obstacle is that tree pointers only go **down**, and half the answer lives
above the target. Every attempt to fix that inside the tree abstraction — a
recursion returning "distance from the target if it is in this subtree, else
−1", then descending the *other* child at the complementary depth — is workable
but fiddly, with an off-by-one at every ancestor.

Change abstraction instead:

> A binary tree is an undirected graph with a maximum degree of three. Distance
> in a graph is BFS.

One pass records each node's parent, and every node then has up to three
neighbours: `left`, `right`, `parent`. BFS out from the target, counting levels,
and stop after `k` — the frontier **is** the answer. No depth arithmetic, no
special cases for "target is the root" or "target is a leaf".

The **visited set is not optional**. Without it the search immediately walks
back down the branch it came up from and reports nodes at distance `k − 2` as
though they were at `k`.
""",
        ),
        (
            "Edge cases and the one-pass alternative",
            """
- **`k = 0`** → just the target itself. The loop runs zero times and returns the
  initial frontier, which is exactly right — no special case needed.
- **`k` larger than the tree** → the frontier empties and you return `[]`.
- **Target not present** → `[]` rather than a crash, if you are taking a value.
- **Node values may be 0.** Identity, not truthiness, is what the visited set
  must key on; `if not node` on a node object holding 0 is fine in Python (the
  object is truthy), but `if not node.val` is a bug waiting to happen.
- **Hashing nodes.** A `@dataclass` with the default `eq=True` sets
  `__hash__ = None` and becomes unhashable, so it cannot go into a set. Use
  `eq=False` (identity semantics, which is what you want) or a plain class.

The **O(1)-extra-space alternative** is the annotate-ancestors trick: one DFS
that returns the distance from the current node down to the target, or −1. At
each ancestor at distance `d`, collect everything at depth `k − d` in the *other*
subtree. Same O(n) time, no parent map — worth naming as the follow-up when the
interviewer asks whether you can avoid the extra structure.
""",
        ),
    ],
}


@dataclass(eq=False)  # eq=False keeps identity hashing, so nodes can go in a set
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def distance_k(root: TreeNode | None, target: int, k: int) -> list[int]:
    if root is None:
        return []

    parent: dict[TreeNode, TreeNode | None] = {}
    start: TreeNode | None = None
    stack: list[tuple[TreeNode, TreeNode | None]] = [(root, None)]
    while stack:
        node, above = stack.pop()
        parent[node] = above
        if node.val == target:
            start = node
        if node.left is not None:
            stack.append((node.left, node))
        if node.right is not None:
            stack.append((node.right, node))

    if start is None:
        return []

    seen = {start}
    frontier = [start]
    for _ in range(k):  # k = 0 falls straight through: the target itself
        nxt: list[TreeNode] = []
        for node in frontier:
            for neighbour in (node.left, node.right, parent[node]):
                if neighbour is not None and neighbour not in seen:
                    seen.add(neighbour)  # without this we walk back down our own branch
                    nxt.append(neighbour)
        frontier = nxt

    return [node.val for node in frontier]


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


TREE = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]

CASES = [
    ((TREE, 5, 2), [1, 4, 7]),
    ((TREE, 7, 3), [3, 6]),  # two hops up, then back down the other side
    ((TREE, 3, 1), [1, 5]),
    ((TREE, 3, 0), [3]),
    ((TREE, 0, 2), [3, 8]),  # target value 0 — truthiness tests fail here
    ((TREE, 5, 9), []),
    (([], 1, 0), []),
    (([-1, -2, -3], -1, 1), [-3, -2]),
]


def solve(values: list[int | None], target: int, k: int) -> list[int]:
    return sorted(distance_k(from_level_order(values), target, k))  # any order is valid
