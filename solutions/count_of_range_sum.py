"""Count of Range Sum — LeetCode 327."""

from __future__ import annotations

from bisect import bisect_left, bisect_right

META = {
    "pattern": "segment-tree",
    "insight": "Subarray sums are differences of prefix sums, so the question becomes: for each prefix, how many earlier prefixes fall in a window — a counting query over a live set.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count the subarrays whose sum lies in `[lower, upper]`, inclusive at both ends.
`n` reaches 10⁵ and the values reach ±2³¹, so sums overflow 32 bits — in Java or
C++ the prefix array must be `long`, and saying that unprompted is half the
credit on this problem.

Confirm two things before writing: the range is **inclusive** at both ends, and
subarrays are contiguous and non-empty.
""",
        ),
        (
            "The insight",
            """
Write `P[k]` for the sum of the first `k` elements, `P[0] = 0`. Then the sum of
`nums[i..j-1]` is `P[j] - P[i]`, and the condition becomes

```
lower <= P[j] - P[i] <= upper       for i < j
  <=>  P[j] - upper <= P[i] <= P[j] - lower
```

So sweep `j` from left to right holding the earlier prefixes `P[0..j-1]` in a
structure that answers **"how many stored values land in this closed window"**,
then insert `P[j]`. That is a Fenwick tree over rank-compressed prefix values:
`O(log n)` to insert, `O(log n)` for the window count, `O(n log n)` overall
against the 10¹⁰ operations of the O(n²) double loop.

Compression is what makes the Fenwick usable — the prefix values are spread over
a range of ~10¹⁴, but there are only `n + 1` distinct ones. Sort them, and turn
each window bound into a rank with a binary search: `bisect_left` for the lower
bound (values `>= P[j] - upper`) and `bisect_right - 1` for the upper (values
`<= P[j] - lower`). An empty window shows up as `hi < lo`, and the count is 0.

The merge-sort variant runs in the same time and needs no compression, but the
Fenwick generalises: make the window dynamic, or ask for the maximum instead of
the count, and the sweep survives while the merge does not.
""",
        ),
        (
            "The pitfalls: P[0], and searching only the values you stored",
            """
**`P[0] = 0` is a real prefix and must be in the tree before the first query.**
It is the one that accounts for every subarray starting at index 0. Forget it
and `([0], 0, 0)` returns 0 instead of 1 — the smallest possible test, and the
one that catches this.

**Compress only the prefix values, then bisect the bounds against them.** The
window ends `P[j] - upper` and `P[j] - lower` are usually not prefix values at
all, so do not try to look them up in the rank map — `bisect_left` and
`bisect_right` give the correct rank for values that are absent, which is
exactly what you want. Inserting the bounds into the compressed array as well is
harmless but triples its size for nothing.

Two smaller ones:

- Sweep order is **query then insert**, so that `i < j` strictly and a prefix is
  never counted against itself. With `lower <= 0 <= upper` the wrong order
  reports `n + 1` extra empty subarrays.
- `lower` and `upper` may both be negative, and elements may be zero or negative,
  so no "sums only grow" shortcut and no sliding window. `([-1, -1], -2, -1)` is
  3 and disproves the greedy answer immediately.
""",
        ),
    ],
}


class FenwickCounter:
    def __init__(self, size: int) -> None:
        self.size = size
        self.tree = [0] * (size + 1)  # one-indexed: index 0 has no low bit

    def add(self, index: int) -> None:
        i = index + 1
        while i <= self.size:
            self.tree[i] += 1
            i += i & -i

    def prefix_count(self, index: int) -> int:
        i = index + 1
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & -i
        return total

    def range_count(self, lo: int, hi: int) -> int:
        if hi < lo:
            return 0
        return self.prefix_count(hi) - (self.prefix_count(lo - 1) if lo > 0 else 0)


def count_range_sum(nums: list[int], lower: int, upper: int) -> int:
    prefixes = [0]
    for value in nums:
        prefixes.append(prefixes[-1] + value)

    ranks = sorted(set(prefixes))
    tree = FenwickCounter(len(ranks))

    total = 0
    tree.add(bisect_left(ranks, prefixes[0]))  # P[0] is a real prefix
    for j in range(1, len(prefixes)):
        # Count stored P[i] with P[j] - upper <= P[i] <= P[j] - lower.
        lo = bisect_left(ranks, prefixes[j] - upper)
        hi = bisect_right(ranks, prefixes[j] - lower) - 1
        total += tree.range_count(lo, hi)
        tree.add(bisect_left(ranks, prefixes[j]))  # query first, then insert
    return total


CASES = [
    (([-2, 5, -1], -2, 2), 3),
    (([], 0, 0), 0),
    # The single-element test that catches a missing P[0].
    (([0], 0, 0), 1),
    (([0], 1, 2), 0),
    # All negative, negative window: no sliding-window shortcut survives this.
    (([-1, -1], -2, -1), 3),
    (([1, 2, 3], 3, 5), 3),
    (([1, -1, 1], -10, 10), 6),
    # 64-bit territory: the sums here leave the 32-bit range.
    (([2147483647, -2147483648, -1, 0], -1, 0), 4),
]


def solve(nums: list[int], lower: int, upper: int) -> int:
    return count_range_sum(list(nums), lower, upper)
