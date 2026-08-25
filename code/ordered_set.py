"""Ordered-set and TreeMap patterns.

A whole class of problems needs "the largest key at most X" against a set that
is still changing. Java has `TreeMap.floorKey`. C++ has `std::map::lower_bound`.

**Python has no ordered set in the standard library**, and that is a real
interview decision rather than trivia:

- `sortedcontainers.SortedList` gives O(log n) insert and O(log n) search, but
  it is a third-party package. LeetCode ships it; a CoderPad session may not.
- `bisect` on a plain list gives O(log n) *search* and O(n) *insert*, because
  the list has to shift. Often fine at n <= 10^4, and quadratic beyond.
- A heap gives you the extreme but not the neighbours.

Say which you are using and why. Reaching for `SortedList` without noting the
dependency is the thing to avoid.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right, insort


class OrderedList:
    """A minimal ordered multiset over `bisect`, with the API interviews want.

    O(log n) search, O(n) insert. Written out because it is what you would
    actually type when `sortedcontainers` is unavailable, and because naming
    the O(n) insert honestly is better than pretending it is O(log n).
    """

    def __init__(self, values: list[int] | None = None) -> None:
        self.values = sorted(values or [])

    def add(self, value: int) -> None:
        insort(self.values, value)

    def remove(self, value: int) -> None:
        index = bisect_left(self.values, value)
        if index < len(self.values) and self.values[index] == value:
            self.values.pop(index)

    def floor(self, value: int) -> int | None:
        """Largest element <= value."""
        index = bisect_right(self.values, value)
        return self.values[index - 1] if index else None

    def ceiling(self, value: int) -> int | None:
        """Smallest element >= value."""
        index = bisect_left(self.values, value)
        return self.values[index] if index < len(self.values) else None

    def __len__(self) -> int:
        return len(self.values)


class MyCalendar:
    """Book intervals, rejecting any that overlap an existing booking.

    The canonical ordered-set problem. A new booking `[start, end)` conflicts
    only with its immediate neighbours in sorted order, so two lookups settle
    it — no scan over every booking.
    """

    def __init__(self) -> None:
        self.starts: list[int] = []
        self.ends: list[int] = []

    def book(self, start: int, end: int) -> bool:
        index = bisect_right(self.starts, start)

        # The booking beginning just before us must finish by the time we start.
        if index > 0 and self.ends[index - 1] > start:
            return False
        # The booking beginning just after us must start at or after our end.
        if index < len(self.starts) and self.starts[index] < end:
            return False

        self.starts.insert(index, start)
        self.ends.insert(index, end)
        return True


def contains_nearby_almost_duplicate(
    nums: list[int], index_diff: int, value_diff: int
) -> bool:
    """Any two values within `index_diff` positions and `value_diff` in value?

    The ordered-set solution keeps a sliding window as a sorted structure and
    asks for the ceiling of `value - value_diff`. The bucketing solution is
    O(n): put each value in a bucket of width `value_diff + 1`, so a collision
    in the same bucket is an immediate hit and only the two adjacent buckets
    need checking.

    Bucketing is used here because it is the better answer and because it
    sidesteps the missing-ordered-set problem entirely.
    """
    if value_diff < 0 or index_diff <= 0:
        return False

    width = value_diff + 1
    buckets: dict[int, int] = {}

    for i, value in enumerate(nums):
        # Floor division keeps negative values in the right bucket.
        key = value // width

        if key in buckets:
            return True
        if key - 1 in buckets and value - buckets[key - 1] < width:
            return True
        if key + 1 in buckets and buckets[key + 1] - value < width:
            return True

        buckets[key] = value
        if i >= index_diff:
            del buckets[nums[i - index_diff] // width]

    return False


CASES = [
    (([1, 2, 3, 1], 3, 0), True),
    (([1, 5, 9, 1, 5, 9], 2, 3), False),
    (([1, 2], 1, 1), True),
    (([1], 1, 1), False),
]


def solve(nums: list[int], index_diff: int, value_diff: int) -> bool:
    return contains_nearby_almost_duplicate(nums, index_diff, value_diff)


def check() -> None:
    for args, expected in CASES:
        assert contains_nearby_almost_duplicate(*args) == expected

    ordered = OrderedList([1, 3, 5, 7])
    assert ordered.floor(4) == 3
    assert ordered.ceiling(4) == 5
    assert ordered.floor(1) == 1
    assert ordered.ceiling(7) == 7
    assert ordered.floor(0) is None
    assert ordered.ceiling(8) is None
    ordered.add(4)
    assert ordered.floor(4) == 4
    ordered.remove(4)
    assert ordered.floor(4) == 3
    assert len(ordered) == 4

    calendar = MyCalendar()
    assert calendar.book(10, 20) is True
    assert calendar.book(15, 25) is False  # overlaps
    assert calendar.book(20, 30) is True  # touching is not overlapping
    assert calendar.book(5, 10) is True
    assert calendar.book(8, 12) is False
