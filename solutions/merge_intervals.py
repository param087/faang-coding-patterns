"""Merge Intervals — LeetCode 56."""

from __future__ import annotations

META = {
    "pattern": "intervals",
    "insight": "After sorting by start, anything that overlaps must overlap the most recent interval — so one pass suffices.",
    "time": "O(n log n)",
    "space": "O(n) for the output",
    "sections": [
        (
            "What it asks",
            """
Merge all overlapping intervals and return the non-overlapping result.

Ask: is the input sorted (no); do **touching** intervals merge — does `[1,4]`
join `[4,5]` (usually yes here, but it is a genuine ambiguity worth
confirming); may I modify the input; are degenerate intervals like `[3,3]`
possible.
""",
        ),
        (
            "The insight",
            """
Sort by **start**. Then any interval that overlaps the current one must
overlap the **most recent** merged interval — because everything before it
started earlier and has already been absorbed.

That is what makes a single pass sufficient: you never need a pairwise
comparison, only a comparison against the last thing you emitted.
""",
        ),
        (
            "The `max` that matters",
            """
When extending, the new end is `max(last_end, end)`, not simply `end`.

A fully contained interval — `[[1,4],[2,3]]` — would otherwise *shrink* the
merged interval to `[1,3]`. Plain assignment passes the sample and fails this.
Run it.
""",
        ),
        (
            "Dry run",
            """
`[[1,3],[2,6],[8,10],[15,18]]`

- `[1,3]` opens the current interval.
- `[2,6]` starts at 2 ≤ 3 → extend to `[1,6]`.
- `[8,10]` starts past 6 → push a new interval.
- `[15,18]` → push.

Also run `[[1,4],[0,4]]` to prove the sort is doing work, and `[[1,4],[2,3]]`
for the containment case.
""",
        ),
        (
            "Follow-ups",
            """
- **Insert Interval** — the list is already sorted and you place one new
  interval in O(n) without re-sorting.
- **Non-overlapping Intervals** — fewest removals, which sorts by **end** and
  is greedy. The different sort key is the point.
- **Employee Free Time** — merge across many sorted lists, then take the gaps.
""",
        ),
    ],
}


def merge(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda x: x[0])
    merged = [ordered[0][:]]  # copy: don't mutate the caller's list

    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            # max, not assignment: a contained interval must not shrink this one.
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged


CASES = [
    (([[1, 3], [2, 6], [8, 10], [15, 18]],), [[1, 6], [8, 10], [15, 18]]),
    (([[1, 4], [4, 5]],), [[1, 5]]),
    (([[1, 4], [2, 3]],), [[1, 4]]),
    (([[1, 4], [0, 4]],), [[0, 4]]),
    (([[1, 4], [0, 0]],), [[0, 0], [1, 4]]),
    (([],), []),
]


def solve(intervals: list[list[int]]) -> list[list[int]]:
    return merge(intervals)
