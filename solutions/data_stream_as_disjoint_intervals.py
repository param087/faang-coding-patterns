"""Data Stream as Disjoint Intervals — LeetCode 352."""

from __future__ import annotations

from bisect import bisect_right

META = {
    "pattern": "intervals",
    "symbol": "SummaryRanges",
    "insight": "Keep the stream merged as it arrives: a new value can only touch the interval just before it and the one just after.",
    "time": "O(log n) to locate plus O(n) for the list splice per addNum; O(n) for getIntervals",
    "space": "O(n) — one entry per disjoint interval, not per value",
    "sections": [
        (
            "What it asks",
            """
`addNum(value)` feeds integers in from a stream; `getIntervals()` returns the
values seen so far summarised as a sorted list of disjoint intervals.

Ask the **call mix** first, because it changes the answer outright:

- if `getIntervals` is rare, keep a `set` of values and build the summary on
  demand — O(1) add, O(n log n) per query, and much less code;
- if it is called after every add, the summary must be maintained
  incrementally, which is what follows.

Also ask whether repeats occur. They do, and a repeat must be a no-op.
""",
        ),
        (
            "The insight",
            """
Hold the intervals in the **canonical** form: sorted, disjoint, and never
touching — `[1,1]` and `[2,2]` are stored as `[1,2]`, never as two entries.

That invariant is the whole trick. Because no two stored intervals are
adjacent, a new value can interact with at most **two** of them: the last
interval starting at or before it, and the first one starting after. One
`bisect` finds that seam, and there are only five outcomes:

| situation | action |
| --- | --- |
| the left neighbour already contains it | no-op |
| it sits one past the left neighbour's end | extend that end |
| it sits one before the right neighbour's start | extend that start |
| both | bridge them, delete one entry |
| neither | insert `[value, value]` |

A version that keeps un-merged intervals loses this bound and has to rescan.
""",
        ),
        (
            "Where it breaks, and what to say about O(n)",
            """
Two cases catch a first attempt:

- **Bridging.** With `[1,1]` and `[3,3]` stored, `addNum(2)` must produce a
  single `[1,3]`, not `[1,2]` plus `[3,3]`. Handle it before the two
  single-sided extensions, and remember to delete the absorbed entry.
- **Repeats.** The stream has duplicates. Check "already covered" first and
  return; otherwise `addNum(1)` twice yields `[1,1]` twice and the invariant
  is gone from then on.

Off-by-one: the merge test is `end + 1 == value`, not `end == value`. These
are *integer* intervals, so adjacency is what merges, not overlap.

On complexity, be honest: the search is O(log n) but `insert`/`pop` on a
Python list is O(n) memmove, so a single add is O(n). With 3·10⁴ calls that is
fine, and a run of merging values makes the list *shrink*. The principled
answer is a balanced BST keyed by start — `TreeMap` in Java,
`sortedcontainers.SortedList` in Python — for a genuine O(log n) add. Say it,
then write the list version, because it is the one you can finish.
""",
        ),
    ],
}


class SummaryRanges:
    def __init__(self) -> None:
        # Sorted, disjoint and never touching: [1,1] and [2,2] are stored [1,2].
        self._intervals: list[list[int]] = []

    def add_num(self, value: int) -> None:
        intervals = self._intervals
        # First interval starting strictly after `value`; i - 1 is its left neighbour.
        i = bisect_right(intervals, value, key=lambda interval: interval[0])

        if i > 0 and intervals[i - 1][1] >= value:
            return  # already covered — the duplicate guard

        # Adjacency, not overlap: these are integers, so end + 1 == value merges.
        joins_left = i > 0 and intervals[i - 1][1] + 1 == value
        joins_right = i < len(intervals) and intervals[i][0] == value + 1

        if joins_left and joins_right:
            intervals[i - 1][1] = intervals[i][1]  # bridge the gap
            intervals.pop(i)
        elif joins_left:
            intervals[i - 1][1] = value
        elif joins_right:
            intervals[i][0] = value
        else:
            intervals.insert(i, [value, value])

    def get_intervals(self) -> list[list[int]]:
        return [interval[:] for interval in self._intervals]  # copies: callers mutate


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    ranges = SummaryRanges()
    assert ranges.get_intervals() == []

    ranges.add_num(1)
    assert ranges.get_intervals() == [[1, 1]]
    ranges.add_num(3)
    assert ranges.get_intervals() == [[1, 1], [3, 3]]
    ranges.add_num(7)
    assert ranges.get_intervals() == [[1, 1], [3, 3], [7, 7]]
    ranges.add_num(2)  # bridges [1,1] and [3,3]
    assert ranges.get_intervals() == [[1, 3], [7, 7]]
    ranges.add_num(6)  # extends [7,7] leftwards
    assert ranges.get_intervals() == [[1, 3], [6, 7]]

    # Repeats must be no-ops, including on an interior value.
    ranges.add_num(2)
    ranges.add_num(1)
    ranges.add_num(7)
    assert ranges.get_intervals() == [[1, 3], [6, 7]]

    # The returned list is a copy — mutating it must not corrupt the state.
    snapshot = ranges.get_intervals()
    snapshot[0][1] = 99
    assert ranges.get_intervals() == [[1, 3], [6, 7]]

    # Descending arrivals exercise the "extend the right neighbour" branch only.
    descending = SummaryRanges()
    for value in (5, 4, 3, 2, 1):
        descending.add_num(value)
    assert descending.get_intervals() == [[1, 5]]

    # Negatives, and a bridge across zero.
    signed = SummaryRanges()
    for value in (-3, -1, 1, 0, -2):
        signed.add_num(value)
    assert signed.get_intervals() == [[-3, 1]]

    # Every other integer: nothing ever merges, so n singletons survive.
    sparse = SummaryRanges()
    for value in range(0, 20, 2):
        sparse.add_num(value)
    assert sparse.get_intervals() == [[v, v] for v in range(0, 20, 2)]
    # Now fill the gaps in reverse; the list collapses to one interval.
    for value in range(19, 0, -2):
        sparse.add_num(value)
    assert sparse.get_intervals() == [[0, 19]]
