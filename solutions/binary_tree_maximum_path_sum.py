"""Binary Tree Maximum Path Sum — LeetCode 124."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-trees",
    "symbol": "max_path_sum",
    "insight": "Return the best straight branch to the parent, record the best bending path on the side, and clamp negative branches to zero.",
    "time": "O(n)",
    "space": "O(h)",
    "sections": [
        (
            "What it asks",
            """
The maximum sum over any path in the tree, where a path is a sequence of nodes
connected by parent–child edges, each node used at most once. It does **not**
have to touch the root, and it does not have to end at a leaf.

Three questions worth asking, and each one changes the code:

- **Can the path be a single node?** Yes — so an all-negative tree answers with
  its largest single value, not 0.
- **Are values negative?** Yes, −1000 to 1000. That is the whole difficulty.
- **Does the path have to include the root?** No. If it did, the problem
  collapses to two independent downward maxima.

Also fix the vocabulary before you start: a path **bends** at most once, at its
topmost node. That single sentence is the algorithm.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Fix each node as the bend point and compute the best downward branch on each
side. Each downward-maximum query walks its subtree, so the query is O(n) and
you run it at n nodes: **O(n²)**.

LeetCode allows 3·10⁴ nodes, so that is roughly 9·10⁸ node visits on a skewed
tree — tens of seconds in Python, and it times out. Enumerating paths directly
is far worse: a complete tree has Θ(n²) node pairs and you would re-walk each.

The redundancy is obvious once named: a single post-order traversal already
computes every downward maximum exactly once. You are recomputing them n times.
""",
        ),
        (
            "The insight",
            """
Two different quantities, and confusing them is why this problem is Hard:

> **What the parent can use is not what the answer is.**

The parent can only extend a path *downward through you*, so what it needs is a
**straight branch**: your value plus the better of your two children's branches.
A path that bends at you goes down the left and down the right — the parent
cannot attach to that without reusing you.

So the recursion returns one thing and records another:

```python
gain(node) = node.val + max(gain(left), gain(right), 0)   # returned upward
best       = max(best, node.val + left_gain + right_gain) # recorded on the side
```

`best` lives in a `nonlocal` (or an instance attribute, or a one-element list —
say which and move on). One post-order pass, every node visited once, O(n).

This is the same skeleton as Diameter of Binary Tree with values in place of
edge counts. If you have done that one, say so; it buys credibility and time.
""",
        ),
        (
            "The two details that actually decide it",
            """
**1. Clamp each branch at zero.** `max(gain(child), 0)` means "if this branch
is a net loss, do not take it". Without the clamp, `[2,-1]` returns 1 — the
algorithm drags a −1 along because it thinks it must reach a leaf. Nothing says
a path ends at a leaf, so dropping the branch is legal, and it is the only way
a negative subtree stops poisoning its ancestors.

**2. Seed `best` at −infinity, not 0.** The clamp handles *branches*; it must
not touch the *answer*. On `[-3]` the answer is −3, and a `best = 0` seed
returns 0 — a path of zero nodes, which the problem forbids. This is the single
most common wrong submission, and it passes every example in the problem
statement because every example contains a positive number.

Keep the two straight: clamp what you pass **up**, never clamp what you
**record**. The recorded candidate is always `node.val + left + right` where
`left` and `right` are already clamped, so a lone negative node still
contributes itself.
""",
        ),
        (
            "Dry run",
            """
`[-10, 9, 20, null, null, 15, 7]`

- `gain(9) = 9`, and it records the candidate 9.
- `gain(15) = 15`, `gain(7) = 7`.
- At 20: both children clamp to themselves, so the bending candidate is
  `20 + 15 + 7 = 42`. It returns `20 + max(15, 7) = 35` upward — **not 42**,
  because −10 cannot attach to a path that already uses both sides of 20.
- At −10: candidate `−10 + 9 + 35 = 34`. Returns `−10 + 35 = 25`.

Answer **42**, and it never touches the root. Returning 34 instead is the
signature of code that recorded the returned value rather than the bend.

Now `[2, -1]`: `gain(-1) = -1`, clamped to 0 at the parent, so the candidate at
2 is `2 + 0 + 0 = 2`. And `[-2, -1]`: the candidates are −1 (at the leaf) and
−2 (at the root, both branches clamped), so the answer is **−1** — an
all-negative tree answering with its largest single value.
""",
        ),
        (
            "Follow-ups",
            """
- **Return the path itself, not the sum.** Store, at each node, which branch
  won, then reconstruct downward from the recorded bend point. Say up front
  that you need a pointer to the bend node, not just the value.
- **Diameter of Binary Tree (543)** — literally this function with every value
  set to 1 and the clamp removed (counts are never negative).
- **Path Sum III (437)** — paths must run strictly downward, so the bend
  disappears and it becomes prefix sums in a hash map along the current root
  path, O(n).
- **Longest Univalue Path (687)** — same skeleton, with the branch dropped
  whenever the child's value differs.
- **N-ary trees** — the bend takes the **two largest** clamped child gains, so
  keep a running top-two rather than a left/right pair.
- **Path must contain the root** — no recursion needed beyond one downward
  maximum per side; a good sanity question to check the interviewer means the
  unconstrained version.
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


def max_path_sum(root: TreeNode | None) -> int:
    if not root:
        return 0  # LeetCode guarantees at least one node; be explicit anyway
    best = float("-inf")  # never 0: an all-negative tree must answer negative

    def gain(node: TreeNode | None) -> int:
        """Best straight downward branch starting at `node`, never negative."""
        nonlocal best
        if not node:
            return 0
        left = max(gain(node.left), 0)  # drop a losing branch
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)  # the path bending here
        return node.val + max(left, right)  # what the parent can extend

    gain(root)
    return int(best)


CASES = [
    (([1, 2, 3],), 6),
    (([-10, 9, 20, None, None, 15, 7],), 42),
    (([-3],), -3),
    (([2, -1],), 2),
    (([-2, -1],), -1),
    (([1, -2, -3],), 1),
    (([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],), 48),
    (([-1, -2, -3],), -1),
]


def solve(values: list[int | None]) -> int:
    return max_path_sum(from_level_order(values))
