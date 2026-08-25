"""Heaps and priority queues.

Three uses cover nearly everything: keep the best k, merge k sorted streams,
and maintain a running median with two heaps facing each other.

`heapq` is a **min**-heap only. For a max-heap, negate on the way in and out —
and say that you are doing so, because silently negated values are where the
bugs hide.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterable


def k_largest(nums: list[int], k: int) -> list[int]:
    """The k largest values, using a min-heap of size k.

    The counter-intuitive part: to keep the *largest* k you use a **min**-heap,
    because the root is then the weakest survivor and the cheapest thing to
    evict. O(n log k), which beats sorting when k is small.
    """
    heap: list[int] = []

    for value in nums:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)  # drop the smallest survivor

    return sorted(heap, reverse=True)


def k_closest_to_origin(points: list[tuple[int, int]], k: int) -> list[tuple[int, int]]:
    """k points closest to the origin.

    Two things worth saying: compare squared distances (no `sqrt`, no floating
    point), and push `(-distance, point)` so a size-k *max*-heap evicts the
    farthest.
    """
    heap: list[tuple[int, tuple[int, int]]] = []

    for x, y in points:
        distance = x * x + y * y
        heapq.heappush(heap, (-distance, (x, y)))
        if len(heap) > k:
            heapq.heappop(heap)

    return [point for _, point in sorted(heap, reverse=True)]


def merge_k_sorted(lists: Iterable[list[int]]) -> list[int]:
    """Merge k sorted lists in O(N log k).

    The heap holds one candidate per list — its head — so it never exceeds k
    entries. Pushing everything and sorting is O(N log N); this is the reason
    the heap is worth the trouble.
    """
    heap: list[tuple[int, int, int]] = []  # (value, list index, position)

    for i, values in enumerate(lists):
        if values:
            heapq.heappush(heap, (values[0], i, 0))

    source = list(lists)
    merged: list[int] = []
    while heap:
        value, i, position = heapq.heappop(heap)
        merged.append(value)
        if position + 1 < len(source[i]):
            heapq.heappush(heap, (source[i][position + 1], i, position + 1))

    return merged


class MedianFinder:
    """Running median of a stream, in O(log n) per insert.

    Two heaps facing each other: a max-heap of the smaller half (negated) and
    a min-heap of the larger half. The invariant is that `low` holds the same
    number of elements as `high`, or exactly one more.

    Pushing through the *other* heap first is what keeps the halves correct —
    a value must be compared against the opposite side before it settles.
    """

    def __init__(self) -> None:
        self._low: list[int] = []  # max-heap via negation
        self._high: list[int] = []  # min-heap

    def add(self, value: int) -> None:
        heapq.heappush(self._low, -heapq.heappushpop(self._high, value))
        if len(self._low) > len(self._high) + 1:
            heapq.heappush(self._high, -heapq.heappop(self._low))

    def median(self) -> float:
        if len(self._low) > len(self._high):
            return float(-self._low[0])
        return (-self._low[0] + self._high[0]) / 2


CASES = [
    (([3, 2, 1, 5, 6, 4], 2), [6, 5]),
    (([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), [6, 5, 5, 4]),
    (([1], 1), [1]),
]


def solve(nums: list[int], k: int) -> list[int]:
    return k_largest(nums, k)


def check() -> None:
    for args, expected in CASES:
        assert k_largest(*args) == expected

    assert k_closest_to_origin([(1, 3), (-2, 2)], 1) == [(-2, 2)]
    assert sorted(k_closest_to_origin([(3, 3), (5, -1), (-2, 4)], 2)) == [(-2, 4), (3, 3)]

    assert merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]]) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert merge_k_sorted([]) == []
    assert merge_k_sorted([[], [1]]) == [1]

    finder = MedianFinder()
    finder.add(1)
    assert finder.median() == 1.0
    finder.add(2)
    assert finder.median() == 1.5
    finder.add(3)
    assert finder.median() == 2.0
    finder.add(0)
    assert finder.median() == 1.5
