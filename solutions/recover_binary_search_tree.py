"""Recover Binary Search Tree — LeetCode 99."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "recover_tree",
    "insight": "Two swapped nodes produce one or two descents in the sorted in-order sequence; take the first descent's left and the last descent's right.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Exactly two nodes of a BST had their values exchanged. Restore the tree
**without changing its structure** — only two values move.

Two clarifications worth making. First: is it exactly two, guaranteed? Yes, and
that guarantee is what makes a single pass sufficient — with k unknown swaps
you would be sorting the in-order sequence and writing it back. Second: may I
swap values, or must I relink nodes? Values is standard and much simpler; if
nodes carry extra payload, relinking is the honest answer and the interviewer
will usually say values are fine.

The published follow-up asks for **O(1) space**, which is Morris traversal.
""",
        ),
        (
            "The insight",
            """
In-order the tree. If it were intact the sequence would be strictly increasing;
one swap of two elements in a sorted array creates a very specific signature.

Call a position where `previous > current` a **descent**. Swapping two elements
of a sorted sequence produces either one or two descents, never more:

- **Two descents** when the swapped elements are not adjacent, e.g.
  `1 2 3 4 5` → `1 5 3 4 2`: descents at `5 > 3` and `4 > 2`. The culprits are
  the **larger** value of the first descent (5) and the **smaller** value of the
  last (2).
- **One descent** when they are adjacent, e.g. `1 2 3 4 5` → `1 3 2 4 5`: the
  single descent `3 > 2` names both culprits at once.

So sweep in-order carrying `previous`. On the first descent record
`first = previous`; on **every** descent record `second = current`. At the end,
exchange their values. One pass, no extra array.

Do not stop after the first descent. In the two-descent case you would swap the
wrong pair, and the tree stays broken — but subtly, in a way that still passes
a naive root-and-children check.
""",
        ),
        (
            "The adjacent-swap case",
            """
This is the case that decides the problem, and it is why `second` is assigned
unconditionally rather than only on the second descent.

If the two swapped nodes are **neighbours in the in-order sequence** there is
only one descent, and both culprits sit inside it: `first = previous` and
`second = current`, set on the same iteration. Code written as "first descent
gives `first`, second descent gives `second`" leaves `second` as `None`, then
crashes or no-ops.

The minimal example is a two-node tree: values `1` and `2` with `2` as the left
child of `1`. In-order reads `2, 1` — a single descent, and swapping the pair it
names fixes the tree.

Two smaller traps in the same loop:

- Compare against the previous **in-order** node, not the parent. A parent
  comparison is the local check that fails
  [Validate BST](../../solutions/validate-binary-search-tree/) for the same
  reason.
- Recursion is fine at n ≤ 1000, but the iterative stack version is what you
  extend to Morris for the O(1)-space follow-up: thread each node's predecessor
  right pointer to itself, walk, then unthread. It mutates the tree during the
  traversal, so it is unusable under concurrent reads — say that trade-off.
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


def recover_tree(root: TreeNode | None) -> None:
    stack: list[TreeNode] = []
    node = root
    previous: TreeNode | None = None
    first: TreeNode | None = None
    second: TreeNode | None = None

    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()

        if previous is not None and previous.val > node.val:
            if first is None:
                first = previous  # larger value of the first descent
            second = node  # every descent — the adjacent case needs this
        previous = node
        node = node.right

    if first is not None and second is not None:
        first.val, second.val = second.val, first.val


CASES = [
    (([1, 3, None, None, 2],), [3, 1, None, None, 2]),
    (([3, 1, 4, None, None, 2],), [2, 1, 4, None, None, 3]),
    (([1, 2],), [2, 1]),  # adjacent swap: only one descent
    (([2, 3, 1],), [2, 1, 3]),  # the two leaves swapped
    (([3, 2, 4, 5, None, None, 1],), [3, 2, 4, 1, None, None, 5]),
    (([4, 2, 6, 7, 3, 5, 1],), [4, 2, 6, 1, 3, 5, 7]),  # far-apart swap
    (([1],), [1]),
    (([],), []),
]


def solve(values: list[int | None]) -> list[int | None]:
    root = from_level_order(values)  # fresh tree each run: recover_tree mutates
    recover_tree(root)
    return to_level_order(root)
