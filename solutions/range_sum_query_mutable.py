"""Range Sum Query - Mutable — LeetCode 307."""

from __future__ import annotations

META = {
    "pattern": "segment-tree",
    "symbol": "NumArray",
    "insight": "A plain array is O(n) per query; a prefix-sum array is O(n) per update. A Fenwick tree makes both O(log n).",
    "time": "O(n) build, O(log n) per update and query",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Support `update(index, value)` and `sumRange(left, right)` on an array, with
both operations happening often.

Ask: how many updates versus queries? (If updates are rare, prefix sums with
periodic rebuilds might genuinely win — asking shows judgement rather than
reflex.) Is the range inclusive? Are values bounded?
""",
        ),
        (
            "State the tension first",
            """
This is the motivation, and naming it is how you show you understand *why*
the structure exists:

- A **plain array**: O(1) update, **O(n) query**.
- A **prefix-sum array**: O(1) query, **O(n) update**.

Whichever you pick, the other operation is too slow. That tension is what the
log-time structure resolves.
""",
        ),
        (
            "Which structure",
            """
**Fenwick tree**, because the operation is a sum and therefore **invertible** —
a range sum is the difference of two prefix sums.

Say why you did not reach for a segment tree: you would need one for min, max
or gcd, where there is no "subtract" and the difference trick fails. Choosing
the simpler structure deliberately is the signal.
""",
        ),
        (
            "The index arithmetic",
            """
`i & -i` isolates the lowest set bit, which is the size of the range each node
covers. Adding it walks *up* for updates; subtracting it walks *down* for
queries.

**One-indexed internally, always.** Index 0 has no lowest set bit, so
`i -= i & -i` never terminates. Every Fenwick implementation adds 1 on the way
in — if yours does not, that is the bug.
""",
        ),
        (
            "update is a delta, not an assignment",
            """
A Fenwick tree adds; it does not assign. So `update(i, v)` must first compute
`v - current[i]` and add *that*, keeping a shadow copy of the raw values.

Forgetting the shadow array is the most common mistake here, and it silently
accumulates rather than replacing.
""",
        ),
        (
            "Follow-ups",
            """
- **Range Sum Query 2D - Mutable** — a 2-D Fenwick, the same arithmetic
  applied on both axes.
- **Range update, range query** — a segment tree with lazy propagation, or two
  Fenwick trees. Recognising that lazy propagation is what is needed, and
  saying so, is usually worth more in a 35-minute round than attempting it.
- **Min or max instead of sum** — not invertible, so a segment tree.
""",
        ),
    ],
}


class FenwickTree:
    def __init__(self, size: int) -> None:
        self.size = size
        self.tree = [0] * (size + 1)  # one-indexed: index 0 has no low bit

    def add(self, index: int, delta: int) -> None:
        i = index + 1
        while i <= self.size:
            self.tree[i] += delta
            i += i & -i  # the next node covering this index

    def prefix_sum(self, index: int) -> int:
        i = index + 1
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & -i  # drop the lowest set bit
        return total


class NumArray:
    def __init__(self, nums: list[int]) -> None:
        # Shadow copy: the tree adds deltas, so we need the raw values.
        self.values = nums[:]
        self.tree = FenwickTree(len(nums))
        for i, value in enumerate(nums):
            self.tree.add(i, value)

    def update(self, index: int, value: int) -> None:
        delta = value - self.values[index]  # a delta, not an assignment
        self.values[index] = value
        self.tree.add(index, delta)

    def sum_range(self, left: int, right: int) -> int:
        upper = self.tree.prefix_sum(right)
        lower = self.tree.prefix_sum(left - 1) if left > 0 else 0
        return upper - lower


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    array = NumArray([1, 3, 5])
    assert array.sum_range(0, 2) == 9
    array.update(1, 2)
    assert array.sum_range(0, 2) == 8
    assert array.sum_range(1, 1) == 2
    assert array.sum_range(0, 0) == 1

    # Repeated updates to the same index must replace, not accumulate.
    array.update(1, 10)
    array.update(1, 4)
    assert array.sum_range(0, 2) == 10

    negatives = NumArray([-1, -2, -3])
    assert negatives.sum_range(0, 2) == -6
    negatives.update(0, 5)
    assert negatives.sum_range(0, 2) == 0

    single = NumArray([7])
    assert single.sum_range(0, 0) == 7
    single.update(0, -7)
    assert single.sum_range(0, 0) == -7

    # Cross-check every range against a brute-force sum.
    raw = [4, -1, 9, 0, 3, 7, -5]
    checked = NumArray(raw)
    checked.update(3, 6)
    raw[3] = 6
    for left in range(len(raw)):
        for right in range(left, len(raw)):
            assert checked.sum_range(left, right) == sum(raw[left : right + 1])
