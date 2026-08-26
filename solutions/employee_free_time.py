"""Employee Free Time — LeetCode 759 (Premium)."""

from __future__ import annotations

import heapq

META = {
    "pattern": "intervals",
    "insight": "Who owns which interval is irrelevant — pour them all into one sorted stream, merge, and the gaps are the answer.",
    "time": "O(n log n) flattened, O(n log k) with a heap merge",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Each employee has a list of busy intervals, sorted and non-overlapping within
that employee. Return the finite intervals of **positive length** during which
*every* employee is free.

LeetCode Premium, so the statement is not public — the task is as described,
and it is a common Google and LinkedIn phone-screen question.

Ask: is the time before the first meeting and after the last one free time?
(**No** — only the gaps between busy periods count, otherwise the answer is
unbounded.) Does a zero-length gap count? (No — `[[1,2],[2,3]]` yields nothing.)
Is each employee's own list guaranteed sorted (yes, and that is the hint that a
k-way merge is on the table).
""",
        ),
        (
            "The insight",
            """
The per-employee structure is a **red herring**. "Free for everyone" means "in
nobody's busy interval", so ownership never enters the answer — pour every
interval into one list, sort by start, merge as in
[Merge Intervals](../merge-intervals/), and emit the gap between each merged
block and the next.

That is five lines and O(n log n), and it is a complete, correct answer. Say so
before optimising.
""",
        ),
        (
            "The k-way merge, and the gap test",
            """
The reason the input is shaped as k sorted lists is that the sort is
**avoidable**. Push the first interval of each employee into a min-heap keyed
by start, pop the earliest, and push that employee's next one: the intervals
come out globally sorted in **O(n log k)** with O(k) working memory. With 10⁴
employees of a few meetings each, log k ≈ 13 against log n ≈ 17 — not a
dramatic win, but it is the streaming version, and it is the answer to "what if
each employee's calendar is a database cursor you cannot materialise?"

Both versions live below and are asserted to agree.

Two details that decide correctness either way:

- `current_end = max(current_end, end)`, not assignment. One employee booked
  `[1,10]` while another has `[2,3]` would otherwise open a phantom free
  interval `[3, …]` — someone is still busy.
- The gap test is `start > current_end`, **strict**. Back-to-back meetings
  leave a zero-length gap that is not free time.
""",
        ),
    ],
}


def employee_free_time(schedule: list[list[list[int]]]) -> list[list[int]]:
    intervals = sorted(
        (interval for employee in schedule for interval in employee),
        key=lambda x: x[0],
    )
    if not intervals:
        return []

    free: list[list[int]] = []
    current_end = intervals[0][1]
    for start, end in intervals[1:]:
        if start > current_end:  # strict: a zero-length gap is not free time
            free.append([current_end, start])
        current_end = max(current_end, end)  # max: containment must not open a gap

    return free


def employee_free_time_heap(schedule: list[list[list[int]]]) -> list[list[int]]:
    """Same answer without the global sort: O(n log k) k-way merge."""
    heap = [
        (employee[0][0], who, 0)  # (start, employee index, position in their list)
        for who, employee in enumerate(schedule)
        if employee
    ]
    heapq.heapify(heap)
    if not heap:
        return []

    free: list[list[int]] = []
    current_end: int | None = None
    while heap:
        start, who, position = heapq.heappop(heap)
        end = schedule[who][position][1]
        if position + 1 < len(schedule[who]):
            heapq.heappush(heap, (schedule[who][position + 1][0], who, position + 1))

        if current_end is None:
            current_end = end
            continue
        if start > current_end:
            free.append([current_end, start])
        current_end = max(current_end, end)

    return free


CASES = [
    (([[[1, 2], [5, 6]], [[1, 3]], [[4, 10]]],), [[3, 4]]),
    (([[[1, 3], [6, 7]], [[2, 4]], [[2, 5], [9, 12]]],), [[5, 6], [7, 9]]),
    (([[[1, 10]], [[2, 3]]],), []),
    (([[[1, 2], [3, 4]]],), [[2, 3]]),
    (([[[1, 2], [2, 3]]],), []),
    (([[[1, 2]]],), []),
    (([],), []),
]


def solve(schedule: list[list[list[int]]]) -> list[list[int]]:
    return employee_free_time(schedule)


def check() -> None:
    for args, expected in CASES:
        assert employee_free_time(*args) == expected
        assert employee_free_time_heap(*args) == expected  # both versions agree
