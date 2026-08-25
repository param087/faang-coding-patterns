"""Segment trees and Fenwick (binary indexed) trees.

The tell is **range query plus point update**. A prefix-sum array answers
range queries in O(1) but costs O(n) per update; a plain array updates in O(1)
but scans in O(n). When both happen often, you need the log-time structure.

Fenwick is a third of the code and handles prefix sums. Segment trees handle
any associative operation — min, max, gcd — and support lazy propagation for
range *updates*. Reach for Fenwick unless you need what only a segment tree
gives you.
"""

from __future__ import annotations

from collections.abc import Callable


class FenwickTree:
    """Prefix sums with point updates, both O(log n).

    The index arithmetic is the whole implementation. `i & -i` isolates the
    lowest set bit, which is the size of the range each node covers — adding
    it walks up for updates, subtracting it walks down for queries.

    One-indexed internally, because index 0 has no lowest set bit and the
    loops would not terminate.
    """

    def __init__(self, size: int) -> None:
        self.size = size
        self.tree = [0] * (size + 1)

    def add(self, index: int, delta: int) -> None:
        """Add `delta` at 0-based `index`."""
        i = index + 1
        while i <= self.size:
            self.tree[i] += delta
            i += i & -i  # next node that covers this index

    def prefix_sum(self, index: int) -> int:
        """Sum of [0, index], 0-based inclusive."""
        i = index + 1
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & -i  # drop the lowest set bit
        return total

    def range_sum(self, left: int, right: int) -> int:
        """Sum of [left, right], 0-based inclusive."""
        return self.prefix_sum(right) - (self.prefix_sum(left - 1) if left else 0)


class SegmentTree:
    """Range query with point update, for any associative operation.

    Iterative and stored in a flat array of size 2n: leaves occupy `[n, 2n)`
    and every internal node `i` combines `2i` and `2i+1`. That layout avoids
    recursion and the usual 4n allocation.
    """

    def __init__(
        self,
        values: list[int],
        combine: Callable[[int, int], int] = lambda a, b: a + b,
        identity: int = 0,
    ) -> None:
        self.n = len(values)
        self.combine = combine
        self.identity = identity
        self.tree = [identity] * (2 * self.n)
        self.tree[self.n :] = values
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = combine(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, index: int, value: int) -> None:
        i = index + self.n
        self.tree[i] = value
        while i > 1:
            i //= 2
            self.tree[i] = self.combine(self.tree[2 * i], self.tree[2 * i + 1])

    def query(self, left: int, right: int) -> int:
        """Combine over [left, right), half-open."""
        result_left = self.identity
        result_right = self.identity
        lo, hi = left + self.n, right + self.n

        while lo < hi:
            # An odd boundary means this node is not fully inside the parent's
            # range, so take it now and step past it.
            if lo & 1:
                result_left = self.combine(result_left, self.tree[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                result_right = self.combine(self.tree[hi], result_right)
            lo //= 2
            hi //= 2

        return self.combine(result_left, result_right)


def count_smaller_after_self(nums: list[int]) -> list[int]:
    """Count of Smaller Numbers After Self, via a Fenwick tree over ranks.

    The reframing that makes it a BIT problem: walk from the right, and ask
    "how many values strictly smaller than this one have I already seen?"
    Compressing values to ranks first keeps the tree size at n regardless of
    how large the values are.
    """
    if not nums:
        return []

    ranks = {value: i for i, value in enumerate(sorted(set(nums)))}
    tree = FenwickTree(len(ranks))
    counts: list[int] = []

    for value in reversed(nums):
        rank = ranks[value]
        counts.append(tree.prefix_sum(rank - 1) if rank else 0)
        tree.add(rank, 1)

    return counts[::-1]


CASES = [
    (([5, 2, 6, 1],), [2, 1, 1, 0]),
    (([-1],), [0]),
    (([-1, -1],), [0, 0]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return count_smaller_after_self(nums)


def check() -> None:
    for args, expected in CASES:
        assert count_smaller_after_self(*args) == expected

    fenwick = FenwickTree(5)
    for i, value in enumerate([1, 2, 3, 4, 5]):
        fenwick.add(i, value)
    assert fenwick.prefix_sum(4) == 15
    assert fenwick.range_sum(1, 3) == 9
    assert fenwick.range_sum(0, 0) == 1
    fenwick.add(2, 10)  # 3 becomes 13
    assert fenwick.range_sum(1, 3) == 19

    tree = SegmentTree([1, 3, 5, 7, 9, 11])
    assert tree.query(1, 4) == 15  # 3 + 5 + 7
    tree.update(1, 10)
    assert tree.query(1, 4) == 22
    assert tree.query(0, 6) == 43

    minimum = SegmentTree([5, 2, 8, 1], combine=min, identity=float("inf"))  # type: ignore[arg-type]
    assert minimum.query(0, 4) == 1
    assert minimum.query(0, 2) == 2
