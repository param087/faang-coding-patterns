"""Meeting Rooms II — LeetCode 253 (Premium)."""

from __future__ import annotations

import heapq

META = {
    "pattern": "intervals",
    "insight": "A min-heap of end times: the root is the room freeing up soonest, so the heap's size is the answer.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given meeting intervals, return the fewest rooms needed to hold all of them.

This one is LeetCode Premium, so the statement is not public — the task is as
described above, and it is asked constantly at Amazon and Google.

Ask: can a room be reused the instant the previous meeting ends (almost always
yes, and it changes `<` to `<=`); are intervals sorted (no); can they be
empty.
""",
        ),
        (
            "The heap solution",
            """
Sort by start time. Keep a min-heap of the **end times** of meetings currently
in progress, so the root is the room freeing up soonest.

For each new meeting: if it starts at or after the earliest end, reuse that
room (`heapreplace`); otherwise open a new one. The heap's size at the end is
the answer.
""",
        ),
        (
            "The sweep solution",
            """
Worth giving as well, because it generalises further.

Turn each meeting into two events: `+1` at its start, `−1` at its end. Sort
the events and track a running total; the peak is the answer.

**The tie-break is the bug.** At equal coordinates, `−1` must sort before
`+1`, or a meeting ending exactly as another begins counts as an overlap.
Sorting `(coordinate, delta)` tuples handles it for free because `−1 < +1` —
a nice thing to point out rather than writing a custom comparator.

Offering both solutions, and saying when you would prefer each, is a strong
mid-level signal. The sweep is what you want when the question drifts to "at
what *time* is it busiest" or "how long is at least three things running".
""",
        ),
        (
            "Dry run",
            """
`[[0,30],[5,10],[15,20]]`

- `[0,30]` opens room 1. Heap `[30]`.
- `[5,10]` starts before 30 → room 2. Heap `[10, 30]`.
- `[15,20]` starts at 15, earliest end is 10 ≤ 15 → **reuse**. Heap `[20, 30]`.

Answer 2. Then run `[[7,10],[2,4]]` to confirm the sort matters — unsorted,
you would open two rooms.
""",
        ),
        (
            "Follow-ups",
            """
- **Which meetings share a room** — store the room index alongside the end
  time in the heap.
- **Meetings arrive as a stream** — an [ordered structure](../../patterns/ordered-set/)
  rather than a sort.
- **Meeting Rooms I** (can one person attend all?) — sort and check adjacent
  pairs, O(n log n) and much simpler.
""",
        ),
    ],
}


def min_meeting_rooms(intervals: list[list[int]]) -> int:
    if not intervals:
        return 0

    rooms: list[int] = []  # end times, min-heap
    for start, end in sorted(intervals, key=lambda x: x[0]):
        if rooms and rooms[0] <= start:
            heapq.heapreplace(rooms, end)  # reuse the room freeing up soonest
        else:
            heapq.heappush(rooms, end)

    return len(rooms)


def max_concurrent(intervals: list[list[int]]) -> int:
    """The sweep-line alternative — same answer, generalises further."""
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort()  # (-1) sorts before (+1) at equal coordinates

    running = peak = 0
    for _, delta in events:
        running += delta
        peak = max(peak, running)
    return peak


CASES = [
    (([[0, 30], [5, 10], [15, 20]],), 2),
    (([[7, 10], [2, 4]],), 1),
    (([[1, 5], [8, 9], [8, 9]],), 2),
    (([[1, 2], [2, 3]],), 1),
    (([],), 0),
]


def solve(intervals: list[list[int]]) -> int:
    return min_meeting_rooms(intervals)


def check() -> None:
    for args, expected in CASES:
        assert min_meeting_rooms(*args) == expected
        assert max_concurrent(*args) == expected  # both solutions agree
