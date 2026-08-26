"""Lowest Common Ancestor of a Binary Tree — LeetCode 236."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "lowest_common_ancestor",
    "insight": "A node that hears back from both children is the meeting point; everything else just passes the report upward.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
The lowest node that has both `p` and `q` as descendants, in a **plain** binary
tree with no ordering guarantee.

Ask: are both nodes guaranteed present (usually yes — if not, you need a second
pass to verify); is there a parent pointer (if yes, it becomes the
intersection-of-two-linked-lists problem instead); **is a node its own
ancestor?** (Yes, by LeetCode's definition.)
""",
        ),
        (
            "The insight",
            """
Six lines, and it looks like it cannot possibly be enough. Read the return
value as a **report**:

> "Did this subtree contain either target — and if so, what is the highest
> relevant node in it?"

- If a node hears back from **both** children, it is the meeting point.
- If only one side reports, pass that report upward unchanged.
- If a node **is** a target, report itself — which correctly makes a node its
  own ancestor.
""",
        ),
        (
            "Why it terminates correctly",
            """
Interviewers ask this, because the function never seems to "stop".

Once a node returns itself as the answer, every ancestor above it sees exactly
**one** non-null child and passes it straight up unchanged. So the first
(deepest) meeting point survives all the way to the root, and no later node can
overwrite it.
""",
        ),
        (
            "Dry run",
            """
`[3,5,1,6,2,0,8]`

- `lca(5, 1)` → 3 hears from both sides → **3**.
- `lca(5, 4)` where 4 is under 5 → node 5 reports itself, nothing else reports
  → **5**. That is the "a node is its own ancestor" case.
""",
        ),
        (
            "Follow-ups",
            """
- **The BST version** is much easier and you should not use this algorithm for
  it: walk down, and the first node whose value sits *between* `p` and `q` is
  the answer. O(h), no recursion. Using the ordering is the point of being told
  it is a BST.
- **Nodes might not exist** — add a flag or count found nodes on the way back.
- **Many queries on a static tree** — preprocess with binary lifting for
  O(log n) per query, or Tarjan's offline LCA.
- **N-ary tree** — same idea, but count how many children reported.
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


def find(root: TreeNode | None, value: int) -> TreeNode | None:
    """Locate a node by value, so the tests can pass real node references."""
    if not root:
        return None
    if root.val == value:
        return root
    return find(root.left, value) or find(root.right, value)


def lowest_common_ancestor(
    root: TreeNode | None, p: TreeNode, q: TreeNode
) -> TreeNode | None:
    # A target reports itself — which makes a node its own ancestor.
    if not root or root is p or root is q:
        return root

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root  # heard from both sides: this is the meeting point
    return left or right  # pass the single report upward


CASES = [
    (([3, 5, 1, 6, 2, 0, 8], 5, 1), 3),
    (([3, 5, 1, 6, 2, 0, 8], 6, 2), 5),
    (([3, 5, 1, 6, 2, 0, 8], 5, 6), 5),  # a node is its own ancestor
    (([3, 5, 1, 6, 2, 0, 8], 7, 4), None),
    (([1, 2], 1, 2), 1),
]


def solve(values: list[int | None], a: int, b: int) -> int | None:
    root = from_level_order(values)
    p, q = find(root, a), find(root, b)
    if p is None or q is None:
        return None
    found = lowest_common_ancestor(root, p, q)
    return found.val if found else None
