"""Subtree of Another Tree — LeetCode 572."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "is_subtree",
    "insight": "Run same-tree at every node, but only at nodes whose value already matches the target root — and know the O(n+m) serialisation escape.",
    "time": "O(n · m) worst case, O(n + m) with serialisation + KMP",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Does `root` contain a subtree identical to `subRoot`? "Subtree" means some node
of `root` **plus every one of its descendants** — not a fragment, not a subset
of the children. `[1,2,3]` does not contain `[1,2]`, because the node `1` in the
big tree drags its right child along.

Ask about the empty `subRoot`. LeetCode guarantees at least one node, so it
never comes up in tests, but "nothing is a subtree of everything" is the
convention worth stating in one breath.
""",
        ),
        (
            "The insight",
            """
Two independent recursions, and keeping them separate is the whole trick:

- `is_same_tree(a, b)` — walks both in lockstep, no searching.
- `is_subtree(node, target)` — tries `is_same_tree` here, then recurses left
  and right.

The common mess is one function that both searches and compares; it ends up
"resetting" the target pointer mid-walk and quietly accepts fragments.

Cost: `is_same_tree` is O(m) and you call it at n nodes, so O(n·m). With
n, m ≤ 2000 that is 4·10⁶ node comparisons — well inside limits, and this is
the answer to write. Guarding the call with `node.val == target.val` makes it
much faster in practice without changing the bound.
""",
        ),
        (
            "The serialisation trap",
            """
The O(n + m) answer is: serialise both trees to strings by pre-order with
**null markers**, then ask whether one is a substring of the other — with KMP,
not `in`, if you want the bound to be honest rather than implementation-defined.

Two ways that goes wrong, and interviewers reach for exactly these:

- **No null markers.** Without them `[1,2]` (left child) and `[1,null,2]`
  serialise identically, so you report a match that is not there.
- **No value delimiter.** `[12]` serialises to `12##` and `[2]` to `2##` —
  and `"2##"` is a substring of `"12##"`. False positive. Prefix every value
  with a separator (`^12##` vs `^2##`) and it goes away.

Those two lines are the difference between "I have seen this trick" and "I can
implement it". The naive O(n·m) with the value guard is the safer thing to
submit under time pressure; mention the linear version and move on.
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
        return p is q
    if p.val != q.val:
        return False
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)


def is_subtree(root: TreeNode | None, sub_root: TreeNode | None) -> bool:
    if not sub_root:
        return True
    if not root:
        return False
    # The value guard skips most of the O(m) comparisons.
    if root.val == sub_root.val and is_same_tree(root, sub_root):
        return True
    return is_subtree(root.left, sub_root) or is_subtree(root.right, sub_root)


CASES = [
    (([3, 4, 5, 1, 2], [4, 1, 2]), True),
    (([3, 4, 5, 1, 2, None, None, None, None, 0], [4, 1, 2]), False),
    (([1, 2, 3], [1, 2]), False),
    (([12], [2]), False),
    (([1, 1], [1]), True),
    (([1, None, 1, None, 1], [1, None, 1]), True),
    (([], [1]), False),
    (([1, 2], [1, None, 2]), False),
]


def solve(root: list[int | None], sub_root: list[int | None]) -> bool:
    return is_subtree(from_level_order(root), from_level_order(sub_root))
