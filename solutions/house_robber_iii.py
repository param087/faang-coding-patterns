"""House Robber III — LeetCode 337."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "dp-advanced",
    "insight": "Each node returns a pair — best with itself robbed, best without — so the parent never has to look past its own children.",
    "time": "O(n)",
    "space": "O(h) recursion stack",
    "sections": [
        (
            "What it asks",
            """
Houses form a binary tree. Robbing a node forbids robbing its **direct
children** (and, by symmetry, its parent). Maximise the total taken.

This is House Robber (198) with the line bent into a tree: "no two adjacent"
now means "no parent–child pair", and the linear left-to-right sweep has
nowhere to go.

Clarify that values are non-negative — LeetCode guarantees 0 ≤ val ≤ 10⁴ — so
you never *want* to skip a node for its own sake, only because of the
constraint. With negative values the answer would still be correct, but the
"always take a leaf" intuition breaks.
""",
        ),
        (
            "Brute force, and why it fails",
            """
The direct translation of the rule:

```
rob(node) = max(node.val + rob(grandchildren),
                rob(children))
```

It is correct and it is exponential, because `rob(children)` re-enters the
grandchildren that the first branch already computed. On a **path-shaped** tree
it is exactly the Fibonacci recursion: `T(n) = T(n-1) + T(n-2)`. At a depth of
only 40 that is around 2·10⁸ calls, and the constraints allow 10⁴ nodes.

The usual patch is `@cache` keyed on the node object. It works — nodes are
hashable by identity — but it needs a hash map the size of the tree, and it
still visits each node from two different parents' perspectives. There is a
version with no memo at all.
""",
        ),
        (
            "The insight",
            """
The exponential blow-up comes from a parent needing to know about its
*grandchildren*. Remove that need: have every node report **two** numbers.

```
take = node.val + left.skip + right.skip     # I am robbed, so children are not
skip = max(left) + max(right)                # I am not, so each child is free
```

`take` is "the best total for this subtree given that this node is robbed";
`skip` is the best given it is not. The parent only ever consults its direct
children's pairs, so one post-order pass touches every node once — O(n), no
memo, no hash map.

Answer: `max(take, skip)` at the root.

This "return a tuple of the states the parent can distinguish" move is the
whole of tree DP. Once you see it here, Binary Tree Maximum Path Sum, Longest
Univalue Path and Distribute Coins in Binary Tree all read the same way.
""",
        ),
        (
            "The line that decides it",
            """
`skip = max(left) + max(right)`, **not** `left.take + right.take`.

Not robbing a node does not oblige you to rob its children. If a subtree does
better by skipping its own root too, you take that. Writing
`left.take + right.take` gives the right answer on both LeetCode examples and
then fails on the four-node path `4 → 1 → 2 → 3`
(`[4, 1, null, 2, null, 3]`): the answer is **7** (rob 4 and 3), but forcing
node 1's skip-value to equal node 2's take-value reports **6**. Examples that
are two levels deep cannot catch this; test a chain.

The mirror-image slip is `take = node.val + max(left) + max(right)`, which
would allow robbing a node and its child. `take` must use the children's
`skip` values only. Two lines, two different `max` placements — say them out
loud when you write them.

Also: return the pair as an actual tuple, not two `nonlocal` accumulators. A
tree DP that mutates shared state is where off-by-one bugs live, and the tuple
version is what generalises to n-ary trees (`sum(max(child) for child in
children)`).
""",
        ),
        (
            "Dry run",
            """
`[3, 2, 3, null, 3, null, 1]`

```
        3
      /   \\
     2     3
      \\      \\
       3       1
```

- Leaf `3` (under 2): `(3, 0)`. Leaf `1` (under the right 3): `(1, 0)`.
- Node `2`: `take = 2 + 0 = 2`, `skip = max(3, 0) = 3` → `(2, 3)`.
  Already interesting — skipping node 2 beats robbing it.
- Right node `3`: `take = 3 + 0 = 3`, `skip = max(1, 0) = 1` → `(3, 1)`.
- Root `3`: `take = 3 + 3 + 1 = 7`, `skip = max(2,3) + max(3,1) = 3 + 3 = 6`.

Answer **7** — root plus the two grandchildren-level 3 and 1. Note that `skip`
lost by one here, and on `[3, 4, 5, 1, 3, null, 1]` it wins 9 to 8. Both
branches are live; neither is a formality.
""",
        ),
        (
            "Follow-ups",
            """
- **Reconstruct which houses were robbed.** Store the winning branch per node
  and walk down from the root, alternating between "must skip children" and
  "children are free".
- **n-ary tree**: `take = val + sum(child.skip)`, `skip = sum(max(child))`.
  Identical shape, and a good check that you understood the pair rather than
  memorised two lines.
- **Deep trees**: recursion is O(h), and a 10⁴-node degenerate tree blows
  Python's 1000-frame default. Either raise the limit or run an explicit
  post-order with a stack — worth mentioning unprompted, because a skewed tree
  is the natural adversarial input here.
- **House Robber II (213)**, the circular array: the same "commit to a case"
  trick, run twice with the first house forced in and forced out.
- **Weighted maximum independent set on a general graph** is NP-hard; this is
  linear only because a tree has no cycles, which is the sentence that explains
  why the pair suffices.
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


def rob(root: TreeNode | None) -> int:
    def walk(node: TreeNode | None) -> tuple[int, int]:
        """(best with `node` robbed, best with `node` skipped)."""
        if node is None:
            return (0, 0)
        left = walk(node.left)
        right = walk(node.right)
        take = node.val + left[1] + right[1]  # children must be skipped
        skip = max(left) + max(right)  # children are free, not forced
        return (take, skip)

    return max(walk(root))


CASES = [
    (([3, 2, 3, None, 3, None, 1],), 7),
    (([3, 4, 5, 1, 3, None, 1],), 9),
    (([2, 1, 3, None, 4],), 7),
    (([4, 1, None, 2, None, 3],), 7),
    (([10, 1, 1, 10, 10, 10, 10],), 50),
    (([1],), 1),
    (([0],), 0),
    (([],), 0),
]


def solve(values: list[int | None]) -> int:
    return rob(from_level_order(values))  # fresh tree per call, so CASES reuse
