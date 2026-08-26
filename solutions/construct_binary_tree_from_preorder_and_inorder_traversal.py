"""Construct Binary Tree from Preorder and Inorder Traversal — LeetCode 105."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "build_tree",
    "insight": "Preorder names the root; inorder says how many nodes sit to its left, and that count splits both arrays.",
    "time": "O(n)",
    "space": "O(n) for the index map, O(h) recursion",
    "sections": [
        (
            "What it asks",
            """
Given the preorder and inorder traversals of a binary tree, rebuild the tree.

Ask whether **values are unique**. LeetCode guarantees it, and the guarantee is
load-bearing: with duplicates the pair of traversals no longer determines a
unique tree (`preorder [1,1]`, `inorder [1,1]` fits two shapes), so the O(1)
value → index lookup this solution depends on is not merely an optimisation,
it is the reason the problem is well posed.
""",
        ),
        (
            "The insight",
            """
Two facts, and the recursion falls out:

- **Preorder** visits root, then all of the left subtree, then all of the right.
  So `preorder[0]` is the root, and the next `k` entries are exactly the left
  subtree, for whatever `k` turns out to be.
- **Inorder** visits left subtree, root, right subtree. So finding the root in
  inorder tells you `k` — the number of nodes left of it.

That is the whole problem: inorder supplies the split point, preorder supplies
the roots in the order you will need them.

The version that separates a strong answer from an adequate one is the
**single moving preorder cursor**. Because preorder emits the entire left
subtree before the right, if you build **left before right** the cursor is
always sitting on the next root you need. No preorder offsets, no slicing.

```
build(lo, hi):            # bounds into inorder
    root = preorder[cursor++]
    mid  = position[root]
    root.left  = build(lo, mid - 1)    # must run first
    root.right = build(mid + 1, hi)
```
""",
        ),
        (
            "The detail that decides it",
            """
The naive write-up is O(n²) twice over: `inorder.index(root)` is a linear scan,
and `preorder[1:k+1]` copies. On a right-skewed tree of 3000 nodes that is
~9·10⁶ operations of pure copying, plus the allocation churn.

Both go away with the same fix — **pass index bounds, never sublists** — plus a
`{value: index}` map built once up front.

Two ways this is commonly got wrong:

- **Building right before left.** The cursor then consumes the right subtree's
  roots into the left subtree. It still "works" on a symmetric test tree, which
  is why it survives a quick trace and fails the real one.
- **Recomputing the left size wrongly.** With bounds it is `mid - lo`; with
  absolute inorder indices people write `mid` and get an off-by-`lo` that only
  shows up in right subtrees.

The sibling problem, **106 (postorder + inorder)**, is the mirror: walk
postorder from the **back**, and build **right before left**.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


def build_tree(preorder: list[int], inorder: list[int]) -> TreeNode | None:
    position = {value: i for i, value in enumerate(inorder)}  # needs unique values
    cursor = 0

    def build(lo: int, hi: int) -> TreeNode | None:
        nonlocal cursor
        if lo > hi:
            return None
        value = preorder[cursor]
        cursor += 1
        node = TreeNode(value)
        mid = position[value]  # everything left of mid is the left subtree
        node.left = build(lo, mid - 1)  # left first, or the cursor desynchronises
        node.right = build(mid + 1, hi)
        return node

    return build(0, len(inorder) - 1)


def to_level_order(root: TreeNode | None) -> list[int | None]:
    if root is None:
        return []
    out: list[int | None] = []
    queue = deque([root])
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


CASES = [
    (([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]), [3, 9, 20, None, None, 15, 7]),
    (([], []), []),
    (([-1], [-1]), [-1]),
    (([1, 2, 3], [3, 2, 1]), [1, 2, None, 3]),  # left spine
    (([1, 2, 3], [1, 2, 3]), [1, None, 2, None, 3]),  # right spine
    (([1, 2, 4, 5, 3, 6], [4, 2, 5, 1, 6, 3]), [1, 2, 3, 4, 5, 6]),
    (([-1, -2, -3], [-2, -1, -3]), [-1, -2, -3]),
]


def solve(preorder: list[int], inorder: list[int]) -> list[int | None]:
    return to_level_order(build_tree(preorder, inorder))
