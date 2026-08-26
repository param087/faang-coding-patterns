"""Insert into a Binary Search Tree — LeetCode 701."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "insert_into_bst",
    "insight": "A search for an absent value ends at exactly the null pointer where it belongs, so insertion is a failed search plus one write.",
    "time": "O(h)",
    "space": "O(1) iterative",
    "sections": [
        (
            "What it asks",
            """
Insert a value into a BST and return the root. The value is guaranteed not to
be present already, and **any valid BST** is accepted — the tree need not stay
balanced.

That last clause is the whole difficulty of the problem, so surface it: "Am I
allowed to insert at a leaf, or do you want the tree rebalanced?" Leaf
insertion is three lines; rebalancing is an AVL or red-black rotation and a
completely different conversation. LeetCode wants the three lines, but the
interviewer often wants to hear that you know the difference.
""",
        ),
        (
            "The insight",
            """
Run the ordinary BST search for the value. Because it is not in the tree, the
search cannot succeed — it walks down until it hits a null pointer. **That
null pointer is precisely the slot where the value belongs**: every ancestor on
the path already compared correctly against it, so hanging a new leaf there
cannot violate the BST property anywhere.

So insertion is a failed search plus one assignment. No rebalancing, no
restructuring, nothing else moves.

The only implementation nuisance is that assigning to `node = TreeNode(val)`
inside Python rebinds a local and updates nothing. You need the **parent** and
which side you came down, so keep a `parent` variable in the iterative version,
or let recursion do it for you by returning the (possibly new) subtree root and
having the caller reassign `node.left = insert(node.left, val)`.
""",
        ),
        (
            "Edge cases",
            """
- **Empty tree** — return a fresh single node. Easy to forget in the iterative
  version, where the `while` loop never runs and `parent` stays `None`.
- **The value already exists** — undefined here by the constraints, but say
  what you would do: either ignore it or keep a count on the node. Blindly
  descending on `<=` will silently create a duplicate and break every later
  search.
- **Degenerate input** — inserting 1, 2, 3, … in order builds a 10⁵-deep chain,
  so the recursive version overflows the stack. Another reason to write the
  loop.
- **Negative values** — ordinary integer comparison; no sentinel tricks.
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


def insert_into_bst(root: TreeNode | None, val: int) -> TreeNode:
    fresh = TreeNode(val)
    if not root:
        return fresh  # empty tree: the new node *is* the root

    parent, node = root, root
    while node:
        parent = node  # remember the side we came from
        node = node.left if val < node.val else node.right

    if val < parent.val:
        parent.left = fresh
    else:
        parent.right = fresh
    return root


CASES = [
    (([4, 2, 7, 1, 3], 5), [4, 2, 7, 1, 3, 5]),
    (([40, 20, 60, 10, 30, 50, 70], 25), [40, 20, 60, 10, 30, 50, 70, None, None, 25]),
    (([], 5), [5]),  # empty tree
    (([1], 0), [1, 0]),
    (([1], 2), [1, None, 2]),
    (([5, 3, 8], 4), [5, 3, 8, None, 4]),  # lands as a right child of a left child
    (([0, -3, 9], -1), [0, -3, 9, None, -1]),  # negatives
]


def solve(values: list[int | None], val: int) -> list[int | None]:
    return to_level_order(insert_into_bst(from_level_order(values), val))
