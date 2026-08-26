"""Serialize and Deserialize BST — LeetCode 449."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

META = {
    "pattern": "binary-search-trees",
    "symbol": "Codec",
    "insight": "A BST needs no null markers: pre-order plus the value bounds already says exactly where each subtree ends.",
    "time": "O(n) to serialize and O(n) to deserialize",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Encode a BST as a string and decode it back to the identical tree. Any format
is allowed; the problem explicitly asks you to keep it **compact**, which is
the whole difference from LeetCode 297 (serialize a general binary tree).

Ask: must the decoded tree be identical in *shape*, or merely hold the same
values (identical — otherwise you could sort and rebuild balanced); are values
distinct (yes for a BST here); how large is n (up to 10⁴, which makes recursion
depth on a degenerate chain a legitimate concern).

Say early that you know 297's answer — pre-order with `#` for nulls — and that
you are going to drop the nulls because the ordering makes them redundant.
That framing is what the question is testing.
""",
        ),
        (
            "The insight",
            """
**Serialize:** pre-order, values separated by spaces. Nothing else. A 7-node
tree becomes `"5 3 2 4 6 8"`-style output, roughly half the bytes of the
null-padded version, and no sentinel value can collide with real data.

**Deserialize:** pre-order alone is ambiguous for a general binary tree, but
for a BST it is not, because the values themselves encode the structure. Walk
the list left to right carrying an open interval `(low, high)`:

- the next value belongs to this position only if `low < value < high`;
- if it does not fit, this position is empty — return without consuming it;
- otherwise take it, then build the left child in `(low, value)` and the right
  child in `(value, high)`.

Each value is examined a constant number of times, so decoding is O(n). The
first value that fails the bound test is the first node of some ancestor's
right subtree, and it stays in the stream for that ancestor to claim — that is
the mechanism replacing the null markers.

An in-order serialisation would *not* work: it is sorted, so it throws the
shape away entirely. Pre-order (or post-order, read backwards) is what carries
it.
""",
        ),
        (
            "Rebuilding in O(n), not O(n²)",
            """
The common answer is: serialize pre-order, then deserialize by inserting each
value into a BST one at a time. It returns the right tree — pre-order insertion
reconstructs the original shape — but it costs **O(n·h)**. On a tree built by
inserting `1..10⁴` in order, h = 10⁴ and that is 10⁸ pointer hops for a
10,000-node input. The bounds version is 10⁴ steps.

Two smaller details that decide the implementation:

- **Parse the string once.** `data.split()` then integer-convert into a list,
  and advance an index. Re-slicing the string, or popping from the front of a
  Python list, quietly reintroduces O(n²).
- **The index must be shared.** `nonlocal` on a plain int, or a `deque` you
  `popleft` from, or an iterator — but a local copy per frame breaks it in a
  way that still passes small tests.

At n = 10⁴ a right-leaning chain also blows CPython's 1000-frame recursion
limit. Mention it; the honest fixes are an explicit stack over the same bounds
logic, or `sys.setrecursionlimit`, and interviewers accept the latter as long
as you saw the problem.
""",
        ),
    ],
}


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None


class Codec:
    def serialize(self, root: TreeNode | None) -> str:
        values: list[str] = []

        def preorder(node: TreeNode | None) -> None:
            if node is None:
                return  # no marker emitted — the bounds recover this on the way back
            values.append(str(node.val))
            preorder(node.left)
            preorder(node.right)

        preorder(root)
        return " ".join(values)

    def deserialize(self, data: str) -> TreeNode | None:
        values = [int(token) for token in data.split()]
        index = 0

        def build(low: float, high: float) -> TreeNode | None:
            nonlocal index
            # A value outside the window belongs to an ancestor, so leave it.
            if index == len(values) or not low < values[index] < high:
                return None
            value = values[index]
            index += 1
            node = TreeNode(value)
            node.left = build(low, value)
            node.right = build(value, high)
            return node

        return build(float("-inf"), float("inf"))


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
    if root is None:
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


CASES = [
    (([2, 1, 3],), [2, 1, 3]),
    (([5, 3, 6, 2, 4, None, 7],), [5, 3, 6, 2, 4, None, 7]),
    (([0, -5, 5, -8, -2, 2, 8],), [0, -5, 5, -8, -2, 2, 8]),  # negatives must survive parsing
    (([1, None, 2, None, 3, None, 4, None, 5],), [1, None, 2, None, 3, None, 4, None, 5]),
    (([5, 4, None, 3, None, 2, None, 1],), [5, 4, None, 3, None, 2, None, 1]),  # left chain
    (([1],), [1]),
    (([],), []),
]


def solve(values: list[int | None]) -> list[int | None]:
    codec = Codec()
    return to_level_order(codec.deserialize(codec.serialize(from_level_order(values))))


def check() -> None:
    for index, (args, expected) in enumerate(CASES):
        actual = solve(*args)
        assert actual == expected, f"case {index}: {actual!r} != {expected!r}"

    codec = Codec()
    # The encoding carries no null markers: one token per node, nothing else.
    tree = from_level_order([5, 3, 6, 2, 4, None, 7])
    encoded = codec.serialize(tree)
    assert encoded.split() == ["5", "3", "2", "4", "6", "7"], encoded
    assert codec.serialize(None) == ""

    # A 1023-node balanced tree round-trips exactly, and encodes one token per node.
    def balanced(lo: int, hi: int) -> TreeNode | None:
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(mid, balanced(lo, mid - 1), balanced(mid + 1, hi))

    big = balanced(1, 1023)
    big_encoded = codec.serialize(big)
    assert len(big_encoded.split()) == 1023
    assert to_level_order(codec.deserialize(big_encoded)) == to_level_order(big)
