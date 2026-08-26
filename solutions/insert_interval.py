"""Insert Interval — LeetCode 57."""

from __future__ import annotations

META = {
    "pattern": "intervals",
    "insight": "The list is already sorted, so the overlapping intervals form one contiguous run — collapse that run and copy the rest.",
    "time": "O(n)",
    "space": "O(n) for the output",
    "sections": [
        (
            "What it asks",
            """
A sorted, non-overlapping list of intervals plus one new interval. Insert it,
merging whatever it touches, and keep the result sorted and non-overlapping.

Ask: do **touching** intervals merge — does inserting `[5,8]` into `[[1,5]]`
give `[[1,8]]` or `[[1,5],[5,8]]`? (Merge, on LeetCode.) May I mutate the
input list? Is the input guaranteed sorted and already disjoint — because if
it is not, this is just [Merge Intervals](../merge-intervals/) and the answer
costs O(n log n).
""",
        ),
        (
            "The insight",
            """
Sorted and disjoint means the intervals the new one overlaps are a **single
contiguous run**. So the scan has three phases and no branching cleverness:

1. Copy everything that **ends before** the new interval starts.
2. Absorb the contiguous run that overlaps: `start = min(...)`, `end = max(...)`.
   Emit that one merged interval.
3. Copy the rest.

The whole thing is O(n) with no sort. Re-sorting and calling merge is the wrong
first answer: it works, but it throws away the one property the problem handed
you and turns O(n) into O(n log n). Interviewers ask this straight after Merge
Intervals precisely to see whether you notice.
""",
        ),
        (
            "The two comparisons that decide it",
            """
Phase 1 advances while `intervals[i][1] < start` — **strict**. If it were
`<=`, an interval ending exactly where the new one begins would be copied
through untouched and you would emit `[[1,5],[5,8]]` instead of `[[1,8]]`.

Phase 2 continues while `intervals[i][0] <= end` — **non-strict**, the mirror
of the same rule at the other end.

Two more things that bite:

- The `max` in phase 2 is not optional. Inserting `[2,3]` into `[[1,5]]` must
  return `[[1,5]]`; plain assignment shrinks it to `[1,3]`.
- The merged interval is appended **unconditionally**, even when the run is
  empty. That is what handles an empty input list, an insert before everything,
  and an insert after everything, without three special cases.
""",
        ),
    ],
}


def insert(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    start, end = new_interval
    result: list[list[int]] = []
    i, n = 0, len(intervals)

    # 1. Everything strictly before the new interval, copied through.
    while i < n and intervals[i][1] < start:
        result.append(intervals[i][:])
        i += 1

    # 2. The contiguous overlapping run collapses into one interval.
    while i < n and intervals[i][0] <= end:
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])  # max: a contained interval must not shrink it
        i += 1
    result.append([start, end])

    # 3. Everything after.
    while i < n:
        result.append(intervals[i][:])
        i += 1

    return result


CASES = [
    (([[1, 3], [6, 9]], [2, 5]), [[1, 5], [6, 9]]),
    (([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]), [[1, 2], [3, 10], [12, 16]]),
    (([], [5, 7]), [[5, 7]]),
    (([[1, 5]], [2, 3]), [[1, 5]]),
    (([[1, 5]], [5, 8]), [[1, 8]]),
    (([[1, 5]], [6, 8]), [[1, 5], [6, 8]]),
    (([[3, 5], [7, 9]], [0, 1]), [[0, 1], [3, 5], [7, 9]]),
    (([[1, 2], [5, 6]], [3, 4]), [[1, 2], [3, 4], [5, 6]]),
]


def solve(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    return insert(intervals, new_interval)
