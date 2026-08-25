"""Intervals and sweep line.

Almost every interval problem is "sort by one endpoint, then walk". Which
endpoint you sort by is the decision: start for merging, end for scheduling,
and both-separately when you are counting overlaps.
"""

from __future__ import annotations

import heapq


def merge(intervals: list[list[int]]) -> list[list[int]]:
    """Merge all overlapping intervals.

    Sort by start, then either extend the last interval or begin a new one.
    Touching intervals ([1,4] and [4,5]) merge here because the test is `<=`;
    ask which the interviewer wants — it is a real ambiguity, not filler.
    """
    if not intervals:
        return []

    ordered = sorted(intervals, key=lambda x: x[0])
    merged = [ordered[0][:]]

    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged


def min_meeting_rooms(intervals: list[list[int]]) -> int:
    """Fewest rooms needed to hold every meeting.

    A min-heap of end times: the root is the room freeing up soonest, so if
    the next meeting starts after it, reuse that room instead of opening one.
    The heap size is the answer.
    """
    if not intervals:
        return 0

    rooms: list[int] = []  # end times, min-heap
    for start, end in sorted(intervals, key=lambda x: x[0]):
        if rooms and rooms[0] <= start:
            heapq.heapreplace(rooms, end)
        else:
            heapq.heappush(rooms, end)

    return len(rooms)


def max_concurrent(intervals: list[list[int]]) -> int:
    """Peak overlap, by sweeping events rather than intervals.

    The other way to solve the meeting-rooms question, and the one that
    generalises: turn each interval into +1 at start and -1 at end, sort the
    events, and track the running total. Ends must sort before starts at the
    same coordinate, or a meeting ending exactly when another begins counts
    as an overlap.
    """
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort()  # (-1) sorts before (+1) at equal coordinates

    running = 0
    peak = 0
    for _, delta in events:
        running += delta
        peak = max(peak, running)
    return peak


def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    """Fewest intervals to remove so the rest do not overlap.

    Sort by *end* and greedily keep. The exchange argument: among the
    intervals that could come next, the one ending soonest leaves the most
    room for everything after it, so keeping it is never worse.
    """
    if not intervals:
        return 0

    kept = 0
    last_end = float("-inf")
    for start, end in sorted(intervals, key=lambda x: x[1]):
        if start >= last_end:
            kept += 1
            last_end = end

    return len(intervals) - kept


CASES = [
    (([[1, 3], [2, 6], [8, 10], [15, 18]],), [[1, 6], [8, 10], [15, 18]]),
    (([[1, 4], [4, 5]],), [[1, 5]]),
    (([[1, 4], [0, 4]],), [[0, 4]]),
    (([],), []),
]


def solve(intervals: list[list[int]]) -> list[list[int]]:
    return merge(intervals)


def check() -> None:
    for args, expected in CASES:
        assert merge(*args) == expected

    assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
    assert min_meeting_rooms([[7, 10], [2, 4]]) == 1
    assert min_meeting_rooms([]) == 0

    assert max_concurrent([[0, 30], [5, 10], [15, 20]]) == 2
    assert max_concurrent([[1, 2], [2, 3]]) == 1  # touching is not overlapping
    assert max_concurrent([]) == 0

    assert erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
    assert erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]) == 2
    assert erase_overlap_intervals([]) == 0
