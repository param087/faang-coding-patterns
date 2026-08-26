"""Maximum Number of Events That Can Be Attended — LeetCode 1353."""

from __future__ import annotations

from heapq import heappop, heappush

META = {
    "pattern": "ordered-set",
    "insight": "Walk the calendar day by day and always take the available event that expires soonest — a min-heap of end days keeps that answer live.",
    "time": "O(n log n + D log n), D = span of days touched",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Each event `[start, end]` can be attended on **any single day** in
`[start, end]` inclusive, and you can attend at most one event per day.
Maximise how many events you attend.

Ask this before writing anything: **does attending an event consume its whole
interval, or one day of it?** One day. Everybody who mis-solves this problem
mis-solves it here — it is not interval scheduling, it is bipartite matching
between events and days, which is why the interval-scheduling greedy (sort by
end, take non-overlapping) gives the wrong answer.

Also: `[2, 2]` is a legal one-day event, two events may share days freely, and
days run to 10⁵.
""",
        ),
        (
            "The insight",
            """
Sweep the calendar one day at a time. On day `d`, the events you may attend are
those with `start <= d <= end`. Among them, attend the one with the **smallest
end day**.

The exchange argument: suppose the optimum attends event `B` on day `d` while
event `A`, also available, expires earlier. Swap them — `A` on day `d`, `B` on
whatever day `A` had, if any. `B` is still available then because it expires no
earlier than `A`. The count never drops, so the earliest-deadline choice is
safe. This is the same argument that makes EDF scheduling optimal.

Keeping "smallest end among the currently available events" live under
insertions is a **min-heap** — and note that this is the case where a heap is
enough and a `TreeMap` is overkill, because you only ever look at one end of
the order. Sort the events by start, push each one's end day as the sweep
reaches its start, discard tops that have already expired, and pop one to
attend it.

O((n + D) log n): each event is pushed and popped once, and the day loop covers
the span, at most 10⁵ days.
""",
        ),
        (
            "Edge cases and the O(n α(n)) version",
            """
- **Discard expired tops before attending, not before pushing.** The order
  inside a day is: admit everything starting today, drop everything that ended
  yesterday, then attend. Reverse the last two and you attend an event a day
  after it expired.
- **`end` is inclusive**, so the expiry test is `heap[0] < day`, not `<=`.
  Off by one here and every one-day event `[d, d]` is dropped.
- **Skip idle days.** When the heap empties, jump `day` straight to the next
  event's start instead of ticking through the gap. Irrelevant at 10⁵ days,
  essential the moment the range becomes 10⁹ — and interviewers do ask.
- **Empty input** returns 0, and the loop must not read `events[0]` first.

The alternative that scales to a 10⁹ day range: sort events by end day and, for
each, take the **first free day `>= start`**, tracked by a union-find "next
free day" map with path compression — O(n α(n)) after the sort, with no
dependence on the calendar span at all. Worth naming; the heap sweep is what to
write unless they push.
""",
        ),
    ],
}


def max_events(events: list[list[int]]) -> int:
    if not events:
        return 0

    ordered = sorted(events)  # by start day
    ends: list[int] = []  # min-heap of end days, the currently available events
    index = 0
    day = ordered[0][0]
    attended = 0

    while index < len(ordered) or ends:
        if not ends and ordered[index][0] > day:
            day = ordered[index][0]  # nothing open: skip the idle stretch

        while index < len(ordered) and ordered[index][0] <= day:
            heappush(ends, ordered[index][1])
            index += 1

        while ends and ends[0] < day:  # inclusive end, so strict <
            heappop(ends)

        if ends:
            heappop(ends)  # the soonest to expire
            attended += 1

        day += 1

    return attended


CASES = [
    (([[1, 2], [2, 3], [3, 4]],), 3),
    (([[1, 2], [2, 3], [3, 4], [1, 2]],), 4),
    (([[1, 4], [4, 4], [2, 2], [3, 4], [1, 1]],), 4),
    (([[1, 5], [1, 5], [1, 5], [2, 3], [2, 3]],), 5),  # deadline order matters
    (([[1, 1], [1, 1], [1, 1]],), 1),  # one day, one event
    (([[3, 3], [1, 1]],), 2),  # unsorted, with an idle day between
    (([[1, 100000]],), 1),
    (([],), 0),
]


def solve(events: list[list[int]]) -> int:
    return max_events(events)
