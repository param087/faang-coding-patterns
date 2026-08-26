"""Kth Smallest Element in a BST — LeetCode 230."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "kth_smallest",
    "insight": "In-order traversal emits a BST in sorted order, so stop it at the k-th node instead of finishing it.",
    "time": "O(h + k) — the descent to the smallest, then k steps",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
Return the k-th smallest value in a BST, 1-indexed.

Ask whether the tree is modified between queries. That is not politeness — it
is the published follow-up, and it changes the answer completely (see below).
Ask whether `k` is guaranteed valid; LeetCode says `1 <= k <= n`, but say what
you would do otherwise rather than indexing off the end.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Collect every value into a list and sort: O(n log n) and O(n) space, and it
ignores the fact that you were handed a BST at all. Answering this way is the
fastest route to a follow-up you did not want.

One step better: full in-order traversal into a list, then index `k - 1`. That
is O(n) and correct — but it visits all n nodes even when `k = 1`. LeetCode
allows n up to 10⁴; a service answering 10⁵ such queries does 10⁹ node visits,
each one a pointer chase through cold memory. The traversal is right; finishing
it is what is wasteful.
""",
        ),
        (
            "The insight",
            """
The in-order traversal of a BST is sorted. That single fact carries almost
every problem in this category, and here it means the k-th node **visited**
in-order is the k-th smallest — no comparison against values needed anywhere.

So do not build the list. Run the traversal with an explicit stack, decrement a
counter at each visit, and return the moment it hits zero. Cost is O(h) to walk
down the left spine plus O(k) visits: **O(h + k)**, not O(n).

The explicit stack is what makes early exit clean. A recursive traversal with a
shared counter can also stop early, but you have to thread the "already found
it" signal back through every frame — an exception, a nonlocal flag, or a
sentinel return. Interviewers read that as not knowing the iterative form.
""",
        ),
        (
            "The invariant that makes the stack version work",
            """
The stack holds exactly the nodes whose **left subtrees are fully processed but
which have not themselves been visited yet** — the left spine of the current
subtree.

Each iteration does three things, in this order:

1. Push everything down the left edge until there is no left child.
2. Pop: that node is the next in sorted order. Visit it.
3. Move to its right child and repeat.

Get the order wrong — visiting before draining the left spine — and you get a
pre-order traversal, which is not sorted, and the bug survives on small
balanced examples where the first few values happen to line up.

Every node is pushed once and popped once, so a full run is O(n) with O(h)
stack, and the early return simply stops it after k pops.
""",
        ),
        (
            "Dry run",
            """
Tree `5(3(2(1), 4), 6)`, in-order `1, 2, 3, 4, 5, 6`, with `k = 3`.

- Push 5, 3, 2, 1 — the left spine. Stack bottom-to-top: `[5, 3, 2, 1]`.
- Pop 1. `k = 2`. Its right child is null.
- Pop 2. `k = 1`. Right child null.
- Pop 3. `k = 0` → **return 3**.

Nodes 4, 5 and 6 are never touched. With `k = 1` on a tree that is one long
right-leaning chain, the loop returns after a single pop while the
collect-everything version walks all n nodes.
""",
        ),
        (
            "Follow-ups",
            """
- **"The BST is modified often and you query k-th frequently"** — this is the
  real question. Augment each node with `size`, the count of nodes in its
  subtree, maintained on insert and delete. Then k-th smallest is a descent:
  at each node compare `k` with `size(node.left) + 1` and go left, stop, or go
  right with `k` reduced. **O(h) per query**, and inserts stay O(h) because
  only the nodes on the insertion path change size. Mention that this is an
  order-statistic tree and that a balanced variant (AVL, red-black) makes it a
  guaranteed O(log n).
- **k-th largest** — mirror the traversal: right, node, left.
- **Unbalanced tree** — nothing here assumes balance, but O(h) becomes O(n) on
  a chain; that is an argument for the augmented balanced tree, not against the
  traversal.
- **Streaming k smallest instead of one** — the same stack, wrapped as an
  iterator; see [BST Iterator](../../solutions/binary-search-tree-iterator/).
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


def kth_smallest(root: TreeNode | None, k: int) -> int | None:
    stack: list[TreeNode] = []
    node = root

    while node or stack:
        while node:  # drain the left spine first — this is what sorts it
            stack.append(node)
            node = node.left
        node = stack.pop()  # next value in sorted order
        k -= 1
        if k == 0:
            return node.val  # early exit: the rest is never visited
        node = node.right

    return None  # k exceeded the node count


CASES = [
    (([3, 1, 4, None, 2], 1), 1),
    (([5, 3, 6, 2, 4, None, None, 1], 3), 3),
    (([1], 1), 1),
    (([1, None, 2, None, 3], 1), 1),  # early exit on a right-leaning chain
    (([4, 2, 7, 1, 3, 6, 9], 5), 6),
    (([4, 2, 7, 1, 3, 6, 9], 7), 9),  # k = n
    (([0, -3, 9, -10, None, 5], 2), -3),  # negatives
    (([1, None, 2], 5), None),  # k out of range
]


def solve(values: list[int | None], k: int) -> int | None:
    return kth_smallest(from_level_order(values), k)
