"""Meeting Rooms — LeetCode 252 (Premium)."""

from __future__ import annotations

from itertools import pairwise

META = {
    "pattern": "intervals",
    "insight": "Once sorted by start, a conflict can only be between neighbours — so one adjacent-pair scan settles it.",
    "time": "O(n log n)",
    "space": "O(n) for the sort",
    "sections": [
        (
            "What it asks",
            """
Given a person's meeting intervals, can they attend all of them? Return a
boolean.

This one is LeetCode Premium, so the statement is not public — the task is as
described above, and it is the warm-up half of
[Meeting Rooms II](../meeting-rooms-ii/).

Ask: is the input sorted (**no**, and forgetting the sort is how this "easy"
gets failed); can a meeting start the instant the previous one ends (yes — so
`[[1,2],[2,3]]` is attendable and the comparison is `<=`); are zero-length
meetings possible.
""",
        ),
        (
            "The insight",
            """
After sorting by start time, **only adjacent pairs can conflict**. If meeting
`i` and meeting `j` overlap with `i + 1 < j`, then meeting `i + 1` starts
between them and overlaps too — so the adjacent pair would already have caught
it. That is the entire argument, and it is what makes one linear scan
sufficient instead of the O(n²) all-pairs comparison.

Sort, then check `previous_end <= next_start` for every neighbouring pair. The
sort dominates at O(n log n); the scan is O(n).
""",
        ),
        (
            "Edge cases and what the interviewer is really after",
            """
- **Empty list, single meeting** → `True`. `pairwise` yields nothing, so
  `all(...)` is vacuously true and no special case is needed.
- **`<=` versus `<`.** Back-to-back meetings are fine. Using `<` reports a
  conflict for `[[1,2],[2,3]]`, and this is the one line reviewers check.
- **Sorting on the whole interval** (`sorted(intervals)`) rather than on the
  start also works here because ties on start still put the shorter meeting
  first, and any tie on start is a conflict regardless of order.

The real purpose of this question is the follow-up: "now return how many rooms
you need." That is Meeting Rooms II — a min-heap of end times, or a sweep of
`+1`/`−1` boundary events. Answer this one in thirty seconds and spend the
time there.
""",
        ),
    ],
}


def can_attend_meetings(intervals: list[list[int]]) -> bool:
    ordered = sorted(intervals, key=lambda x: x[0])
    # <= : a meeting may start exactly when the previous one ends.
    return all(current[1] <= following[0] for current, following in pairwise(ordered))


CASES = [
    (([[0, 30], [5, 10], [15, 20]],), False),
    (([[7, 10], [2, 4]],), True),
    (([[1, 2], [2, 3]],), True),
    (([[9, 10], [4, 9], [4, 17]],), False),
    (([[13, 15], [1, 13]],), True),
    (([[5, 8]],), True),
    (([],), True),
]


def solve(intervals: list[list[int]]) -> bool:
    return can_attend_meetings(intervals)
