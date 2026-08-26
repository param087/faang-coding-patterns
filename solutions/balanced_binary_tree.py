"""Balanced Binary Tree — LeetCode 110."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "is_balanced",
    "insight": "Let the height function return a sentinel -1 the instant a subtree is unbalanced, and one post-order pass replaces n height queries.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Is the tree height-balanced — meaning **every node's** two subtree heights
differ by at most 1? Not the root's. Every node's.

That word "every" is the problem. Read it out loud before you start, because
the natural first answer checks the root and passes both LeetCode examples.
""",
        ),
        (
            "The insight",
            """
The obvious version calls `height()` at every node: O(n) work per node, O(n²)
total, and 5000 nodes in a chain is 2.5·10⁷ node visits for a question that
needs 5000.

The fix is that one post-order pass already computes every height on the way
up — you just need somewhere to put the verdict. Overload the return value:

```
height(node) = -1        if this subtree is unbalanced
             = its height otherwise
```

The moment a child returns `-1`, the parent returns `-1` too, and the failure
rides all the way to the root without any extra plumbing. `-1` is safe as a
sentinel precisely because no real height is negative — the empty tree is 0.

An interviewer who dislikes overloaded returns will accept `(height, ok)` as a
tuple; it is the same algorithm and costs one line.
""",
        ),
        (
            "The wrong first answer",
            """
Checking only `abs(height(left) - height(right)) <= 1` at the root.

Counter-example: root `1`, with a left chain `2 → 3 → 4` and a right chain
`5 → 6 → 7`, both going left the whole way. Both subtrees have height 3, so the
root looks perfectly balanced — but node `2` has a left subtree of height 2 and
no right subtree at all. Unbalanced, and the root-only check says otherwise.
That is `[1,2,5,3,null,6,null,4,null,7]`, and it is in the cases below.

The mirrored mistake is recursing on `is_balanced(left) and is_balanced(right)`
*and* recomputing heights inside each call — correct, but back to O(n²). The
sentinel exists to do both jobs in one traversal.
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


def is_balanced(root: TreeNode | None) -> bool:
    def height(node: TreeNode | None) -> int:
        """Real height, or -1 for "something below here is unbalanced"."""
        if not node:
            return 0
        left = height(node.left)
        if left == -1:
            return -1
        right = height(node.right)
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return height(root) != -1


CASES = [
    (([3, 9, 20, None, None, 15, 7],), True),
    (([1, 2, 2, 3, 3, None, None, 4, 4],), False),
    (([1, 2, 5, 3, None, 6, None, 4, None, 7],), False),  # root looks balanced
    (([],), True),
    (([1],), True),
    (([1, 2],), True),
    (([1, 2, None, 3],), False),
    (([1, 2, 3, 4, 5, 6, 7],), True),
]


def solve(values: list[int | None]) -> bool:
    return is_balanced(from_level_order(values))
