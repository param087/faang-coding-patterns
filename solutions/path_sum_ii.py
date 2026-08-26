"""Path Sum II — LeetCode 113."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "path_sum",
    "insight": "Carry one shared path buffer down and pop on the way out; copy it only at a leaf that lands exactly on the target.",
    "time": "O(n²) worst case — n nodes, and each qualifying path costs O(h) to copy",
    "space": "O(h) for the buffer and the stack, plus the output",
    "sections": [
        (
            "What it asks",
            """
Every **root-to-leaf** path whose values sum to a target, returned as lists of
values. Not the count, not one path — all of them.

Two clarifications that change the code:

- **Can values be negative?** On LeetCode yes, from −1000. That single fact
  kills the pruning instinct: you cannot stop descending when the running sum
  overshoots, because a −500 could be waiting below.
- **What counts as a leaf?** Both children null. A node with one child is not a
  leaf even though it looks like the end of a branch.
""",
        ),
        (
            "The insight",
            """
This is backtracking on a tree, and the shape is worth internalising because
every "enumerate all paths" tree problem is the same five lines:

```
append value          # enter
maybe record          # at a leaf
recurse both children
pop                   # leave — this is the whole trick
```

One buffer, mutated in place, restored on the way out. Building a fresh list at
every node (`path + [node.val]`) also works and reads more cleanly, but it
allocates O(h) at every one of the n nodes rather than only at the O(k) paths
that actually qualify — worth naming the tradeoff out loud, then writing the
version with the `pop`.

Carry the **remaining** target down rather than the running total. Then the
test at a leaf is `remaining == 0`, with nothing to compare against a captured
variable.
""",
        ),
        (
            "Edge cases",
            """
- **Empty tree** → `[]`, whatever the target. The `None` guard has to come
  before the append.
- **Target hit at an internal node.** `root = [1,2]`, `target = 1`: the sum is
  right at the root, but the root is not a leaf, so the answer is `[]`. This is
  the case that catches a solution whose base case is `node is None` — that
  version walks into the null child of node 2 and, worse, records the path
  twice for a node with two null children.
- **Duplicate paths are legal.** `[0,1,1]` with target 1 returns `[[0,1],[0,1]]`
  — two distinct paths that happen to have the same values. Do not deduplicate.
- **Negative-only trees.** `[-2,null,-3]` with target −5 must return
  `[[-2,-3]]`; anything that early-exits on sign fails here.
- **Cousin problems.** *Path Sum I* just needs a boolean, so it can short-circuit
  on the first hit. *Path Sum III* counts paths that start and end anywhere,
  which is a different technique entirely — prefix sums in a hash map along the
  current root-to-node path.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def path_sum(root: TreeNode | None, target: int) -> list[list[int]]:
    paths: list[list[int]] = []
    path: list[int] = []

    def walk(node: TreeNode | None, remaining: int) -> None:
        if node is None:
            return
        path.append(node.val)
        remaining -= node.val
        if node.left is None and node.right is None and remaining == 0:
            paths.append(list(path))  # copy: `path` keeps mutating below
        walk(node.left, remaining)
        walk(node.right, remaining)
        path.pop()  # leave the node exactly as we found it

    walk(root, target)
    return paths


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
    (
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22),
        [[5, 4, 11, 2], [5, 8, 4, 5]],
    ),
    (([1, 2, 3], 3), [[1, 2]]),
    (([1, 2], 1), []),  # target met at an internal node — not a path
    (([], 0), []),
    (([-2, None, -3], -5), [[-2, -3]]),  # negatives: no pruning possible
    (([0, 1, 1], 1), [[0, 1], [0, 1]]),  # two distinct paths, same values
    (([5], 5), [[5]]),
    (([5], 0), []),
]


def solve(values: list[int | None], target: int) -> list[list[int]]:
    return path_sum(from_level_order(values), target)
