"""Same Tree — LeetCode 100."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "is_same_tree",
    "insight": "Walk both trees in lockstep; the three null cases — both, one, neither — are the entire problem.",
    "time": "O(min(n, m))",
    "space": "O(min(h1, h2))",
    "sections": [
        (
            "What it asks",
            """
Are two binary trees identical — same shape *and* same values at every
position? Structure counts: `[1,2]` and `[1,null,2]` hold the same multiset of
values and are **not** the same tree.

This is a five-line problem, and it is on the list because it is the subroutine
inside Subtree of Another Tree, Symmetric Tree and most tree-equality follow-ups.
Get the base cases crisp here and those come free.
""",
        ),
        (
            "The insight",
            """
Recurse on the two roots **together**, not on one tree while searching the
other. Three cases, in this order:

1. Both null → `True`. Two absent subtrees match.
2. Exactly one null → `False`. This is the shape check, and it is the case
   people forget.
3. Values differ → `False`; otherwise recurse on `(l.left, r.left)` and
   `(l.right, r.right)`.

`if not p or not q: return p is q` collapses cases 1 and 2 into one line: if
both are `None` the identity holds, and if only one is, it does not.

Short-circuit `and` means you stop at the first mismatch, so the cost is
O(min(n, m)) rather than O(n) — worth stating, because on two trees that differ
at the root you do exactly one comparison.
""",
        ),
        (
            "Edge cases",
            """
- **Both empty** → `True`. `solve([], [])` must not blow up on `values[0]`.
- **One empty** → `False`.
- **Same values, different shape** — `[1,2]` vs `[1,null,2]`. This is the case
  that catches anyone who compared sorted value lists, or compared a pre-order
  traversal *without null markers*.
- **Mirrored trees** — `[1,2,1]` vs `[1,1,2]` are different trees; if you
  wanted them equal you were solving Symmetric Tree, which is this function run
  on `(root.left, root.right)` with the recursive calls crossed over.
- Values run to ±10⁴, so do not lean on positivity anywhere.
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


def is_same_tree(p: TreeNode | None, q: TreeNode | None) -> bool:
    if not p or not q:
        return p is q  # True only when both are None
    if p.val != q.val:
        return False
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)


CASES = [
    (([1, 2, 3], [1, 2, 3]), True),
    (([1, 2], [1, None, 2]), False),
    (([1, 2, 1], [1, 1, 2]), False),
    (([], []), True),
    (([], [1]), False),
    (([1, 2, 3], [1, 2, 4]), False),
    (([-1, -2, -3], [-1, -2, -3]), True),
    (([1, 2, 3, 4], [1, 2, 3, None, 4]), False),
]


def solve(a: list[int | None], b: list[int | None]) -> bool:
    return is_same_tree(from_level_order(a), from_level_order(b))
