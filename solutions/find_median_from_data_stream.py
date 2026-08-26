"""Find Median from Data Stream — LeetCode 295."""

from __future__ import annotations

import heapq

META = {
    "pattern": "heaps",
    "symbol": "MedianFinder",
    "insight": "You do not need the whole stream sorted — only the boundary, which two heaps facing each other maintain in O(log n).",
    "time": "O(log n) per insert, O(1) per query",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Support `addNum(x)` on a stream and `findMedian()` at any point.

Ask: integers or floats; is the value range bounded; is `findMedian` called
after every insert or occasionally. **The range question matters** — it
unlocks a much better solution and asking it is a strong signal.
""",
        ),
        (
            "The naive answer",
            """
Keep a sorted list and insert with `bisect`: O(log n) to *find* the position
but **O(n)** to shift the list. Median is then O(1).

Say this and why it fails at 5·10⁴ inserts.
""",
        ),
        (
            "The insight",
            """
You never need the whole stream sorted — you only need the **boundary** between
the smaller half and the larger half.

So keep a **max-heap of the smaller half** and a **min-heap of the larger
half**. The median sits at their meeting point: the max-heap's root if the
sizes differ, or the average of both roots if they are equal.

`heapq` is min-only, so the smaller half is stored negated. Say that you are
negating — silently negated values are hard for the interviewer to read.
""",
        ),
        (
            "The one-line insert",
            """
`heappush(low, -heappushpop(high, value))`

This looks like magic and it is worth explaining. **Pushing through the *other*
heap first** is what guarantees correctness: a value must be compared against
the opposite side before it settles, or you can end up with a large value
stranded in the small half.

Then one rebalance keeps the sizes within one of each other.
""",
        ),
        (
            "Dry run",
            """
Add 1: `low=[1]`, median **1**.
Add 2: `low=[1]`, `high=[2]`, median **1.5**.
Add 3: `low=[1,2]`, `high=[3]`, median **2**.
Add 0: `low=[0,1]`, `high=[2,3]`, median **1.5**.

Check the rebalance fires on the third insert — that is the branch under test.
""",
        ),
        (
            "The follow-ups they actually ask",
            """
Both are on LeetCode and both reward having asked about the range up front:

- **"All values are in [0, 100]."** A counting array beats both heaps: O(1)
  insert, O(100) median. Constant factors, but a much simpler structure.
- **"99% of values are in [0, 100]."** Counting array plus two small overflow
  lists for the tails.

And one more: **sliding window median**, where a value also *leaves*. Heaps
cannot delete arbitrarily, so that becomes lazy deletion or an
[ordered multiset](../../patterns/ordered-set/).
""",
        ),
    ],
}


class MedianFinder:
    def __init__(self) -> None:
        self._low: list[int] = []  # smaller half, max-heap via negation
        self._high: list[int] = []  # larger half, min-heap

    def add_num(self, value: int) -> None:
        # Push through the opposite heap first so the value settles correctly.
        heapq.heappush(self._low, -heapq.heappushpop(self._high, value))
        if len(self._low) > len(self._high) + 1:
            heapq.heappush(self._high, -heapq.heappop(self._low))

    def find_median(self) -> float:
        if len(self._low) > len(self._high):
            return float(-self._low[0])
        return (-self._low[0] + self._high[0]) / 2


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    finder = MedianFinder()
    finder.add_num(1)
    assert finder.find_median() == 1.0
    finder.add_num(2)
    assert finder.find_median() == 1.5
    finder.add_num(3)
    assert finder.find_median() == 2.0
    finder.add_num(0)
    assert finder.find_median() == 1.5

    # Descending input exercises the rebalance every time.
    descending = MedianFinder()
    for value in (5, 4, 3, 2, 1):
        descending.add_num(value)
    assert descending.find_median() == 3.0

    negatives = MedianFinder()
    for value in (-1, -2, -3):
        negatives.add_num(value)
    assert negatives.find_median() == -2.0

    duplicates = MedianFinder()
    for value in (2, 2, 2, 2):
        duplicates.add_num(value)
    assert duplicates.find_median() == 2.0
