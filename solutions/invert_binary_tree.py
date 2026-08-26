"""Invert Binary Tree — LeetCode 226."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "invert_tree",
    "insight": "Swapping a node's two children is independent of everything below it, so any traversal order works — but the swap must be simultaneous.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Mirror the tree: every node's left and right subtrees trade places, all the way
down. Return the root.

One clarifying question actually matters here: **in place, or a new tree?**
LeetCode wants in place and returns the same root. In a real codebase you would
usually want a copy, and saying so costs you nothing. The version below is in
place; `solve` rebuilds the tree from the level-order list first so the cases
stay reusable.
""",
        ),
        (
            "The insight",
            """
The transformation at a node — swap its two child pointers — does not depend on
anything you learn from the subtrees, and the subtrees do not care whether the
parent has swapped yet. So the two operations commute, and **pre-order,
post-order and BFS all produce the same tree**.

That independence is the whole content of the problem. Contrast it with
Balanced Binary Tree or Maximum Path Sum, where the parent's decision needs a
value computed below and the post-order is forced.

Because order is free, the BFS version is a legitimate answer and it is the one
to reach for if the interviewer raises the 10⁴-node degenerate-chain point:

```python
queue = deque([root])
while queue:
    node = queue.popleft()
    node.left, node.right = node.right, node.left
    ...
```
""",
        ),
        (
            "The pitfall: sequential assignment",
            """
This is the bug that shows up in interviews far more often than it should:

```python
node.left = invert_tree(node.right)
node.right = invert_tree(node.left)   # WRONG — reads the line above
```

By the second line `node.left` is already the inverted right subtree, so the
right subtree gets duplicated and the original left subtree is dropped. On
`[4,2,7,1,3,6,9]` it produces `[4,7,7,9,6,9,6]` — plausible-looking, which is
exactly what makes it dangerous.

Either stash a temporary, or use a simultaneous tuple assignment
(`node.left, node.right = ...`), which Python evaluates fully on the right
before binding anything on the left.
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


def to_level_order(root: TreeNode | None) -> list[int | None]:
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


def invert_tree(root: TreeNode | None) -> TreeNode | None:
    if not root:
        return None
    # Simultaneous, so neither side reads the other's new value.
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


CASES = [
    (([4, 2, 7, 1, 3, 6, 9],), [4, 7, 2, 9, 6, 3, 1]),
    (([2, 1, 3],), [2, 3, 1]),
    (([],), []),
    (([1],), [1]),
    (([1, 2],), [1, None, 2]),
    (([1, None, 2, None, 3],), [1, 2, None, 3]),
    (([1, 2, 2, 3, None, None, 3],), [1, 2, 2, 3, None, None, 3]),
]


def solve(values: list[int | None]) -> list[int | None]:
    # Rebuild from the plain list, so the in-place invert cannot leak between cases.
    return to_level_order(invert_tree(from_level_order(values)))
