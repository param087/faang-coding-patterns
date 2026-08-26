"""Remove Covered Intervals — LeetCode 1288."""

from __future__ import annotations

META = {
    "pattern": "intervals",
    "insight": "Sort by start ascending and end descending, then an interval is covered exactly when its end fails to beat the furthest end so far.",
    "time": "O(n log n) — the sort dominates, the sweep is O(n)",
    "space": "O(n) for the sorted copy, O(1) extra if you sort in place",
    "sections": [
        (
            "What it asks",
            """
`[a, b]` is **covered** by `[c, d]` when `c <= a` and `b <= d`. Remove every
covered interval and return how many survive.

Ask: are two identical intervals possible (yes — each covers the other, and
exactly one must survive, which is the case that decides your comparison
operator); are endpoints inclusive (yes, so `[1,4]` covers `[1,4]` and
`[2,4]`); may I reorder the input.

Note what coverage is **not**: `[0,10]` and `[5,12]` overlap heavily and
neither is covered. This is not a merge problem.
""",
        ),
        (
            "The insight",
            """
Sort by start. Now every interval you visit starts at or after everything you
have already seen, so the left condition `c <= a` is satisfied by **all** of
them for free. Only the right condition is still open.

And you do not need to test it against each earlier interval — the one that
reaches furthest right dominates every other, because its start is already
at or before yours. So carry a single `furthest` end:

- `end <= furthest` → covered, drop it;
- otherwise it is a survivor, count it and extend `furthest`.

One pass after the sort. The whole problem is choosing the sort key.
""",
        ),
        (
            "The tie-break that decides it",
            """
Sort by `(start, -end)` — start ascending, **end descending**.

With the naive `sorted(intervals)` key, `[[1,2],[1,4]]` visits `[1,2]` first:
`furthest` becomes 2, then `[1,4]` has end 4 > 2 and is counted too. Answer 2,
correct answer 1. The sample cases in the problem do not contain a tie, so
this passes locally and fails on submit.

Putting the longer interval first at equal starts means a tied interval always
meets a `furthest` that already swallows it. That also makes the operator
`end > furthest` (strict) correct for duplicates: `[[1,4],[1,4]]` sees
`4 > 4` as false and counts one.
""",
        ),
    ],
}


def remove_covered_intervals(intervals: list[list[int]]) -> int:
    # Start ascending, end descending: at equal starts the longest comes first,
    # so a tied interval always meets a `furthest` that already covers it.
    ordered = sorted(intervals, key=lambda interval: (interval[0], -interval[1]))

    survivors = 0
    furthest = float("-inf")

    for _, end in ordered:
        if end > furthest:  # strict: an identical repeat is covered
            survivors += 1
            furthest = end

    return survivors


CASES = [
    (([[1, 4], [3, 6], [2, 8]],), 2),
    (([[1, 4], [2, 3]],), 1),
    (([[1, 2], [1, 4], [3, 4]],), 1),  # equal starts — the sort tie-break
    (([[1, 4], [1, 4]],), 1),  # duplicates: exactly one survives
    (([[0, 10], [5, 12]],), 2),  # overlap is not coverage
    (([[3, 10], [4, 10], [5, 11]],), 2),  # shared end, still covered
    (([[1, 2]],), 1),
    (([],), 0),
]


def solve(intervals: list[list[int]]) -> int:
    return remove_covered_intervals(intervals)
