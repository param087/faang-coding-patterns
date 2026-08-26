"""Non-overlapping Intervals — LeetCode 435."""

from __future__ import annotations

META = {
    "pattern": "intervals",
    "insight": "Removing fewest is keeping most, and the interval that finishes earliest always leaves the most room for the rest.",
    "time": "O(n log n)",
    "space": "O(n) for the sort",
    "sections": [
        (
            "What it asks",
            """
Return the minimum number of intervals to remove so that none of the survivors
overlap.

Ask: do intervals that merely **touch** count as overlapping — is `[1,2]` with
`[2,3]` a conflict? (No on LeetCode, and it flips `>` to `>=`.) Are duplicates
possible (yes, and `[[1,2],[1,2]]` costs one removal).
""",
        ),
        (
            "The insight",
            """
Flip the question. **Minimum removed = n − maximum kept**, and "maximum set of
mutually non-overlapping intervals" is textbook activity selection.

Sort by **end**, walk left to right, and keep an interval whenever it starts at
or after the last kept end. Greedy is optimal because of an exchange argument
worth stating out loud: if some optimal solution does not contain the
earliest-finishing interval, swap its first interval for that one — the swap
never ends later, so nothing downstream breaks and the count is unchanged.

Every interval you keep leaves the maximum possible room for whatever follows.
That is the whole algorithm; the code is six lines.
""",
        ),
        (
            "Sorting by start is the wrong first answer",
            """
Sorting by **start** and dropping each conflicting interval as you meet it
fails on `[[1,100],[2,3],[3,4]]`: it keeps `[1,100]`, then discards both
`[2,3]` and `[3,4]` for **2** removals. The answer is **1** — drop `[1,100]`.

You can rescue the start-sorted version by, on a conflict, discarding whichever
of the two ends later (`previous_end = min(previous_end, end)`). That is the
same greedy wearing a disguise, and it is one more line to get wrong under
pressure. Sort by end.

Two more details:

- The comparison is `start >= previous_end`, not `>`. With `>`, `[[1,2],[2,3]]`
  reports 1 removal instead of 0.
- Initialise `previous_end` to `-inf`, not `0` — the coordinates can be
  negative, and a `0` seed silently drops every interval starting below zero.
""",
        ),
    ],
}


def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    kept = 0
    previous_end = float("-inf")  # not 0: coordinates may be negative

    for start, end in sorted(intervals, key=lambda x: x[1]):
        if start >= previous_end:  # >= : touching is not overlapping
            kept += 1
            previous_end = end

    return len(intervals) - kept


CASES = [
    (([[1, 2], [2, 3], [3, 4], [1, 3]],), 1),
    (([[1, 2], [1, 2], [1, 2]],), 2),
    (([[1, 2], [2, 3]],), 0),
    (([[1, 100], [2, 3], [3, 4]],), 1),
    (([[-52, 31], [-73, -26], [82, 97], [-65, -11], [-62, -49], [95, 99]],), 4),
    (([[1, 2]],), 0),
    (([],), 0),
]


def solve(intervals: list[list[int]]) -> int:
    return erase_overlap_intervals(intervals)
