"""Minimum Time to Complete Trips — LeetCode 2187."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Trips completed by time t is a monotone step function you can evaluate in one pass, so binary search t rather than simulating buses.",
    "time": "O(n log(min(time) · totalTrips))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Bus `i` takes `time[i]` per trip and buses run independently and continuously.
Find the least `t` such that the buses together complete at least
`totalTrips` trips.

Worth confirming: buses do **not** wait for each other, and a trip counts only
when finished. Both are implied by the phrasing "the `i`-th bus can make its
next trip immediately after finishing the current one", and both are what make
the count a clean `t // time[i]` rather than a scheduling problem.
""",
        ),
        (
            "The insight",
            """
`trips(t) = sum(t // time[i])` — floor division, since a trip half-finished at
time `t` does not count. That function is **non-decreasing** in `t`, so the
times that reach `totalTrips` form a suffix and you binary search its start.

Note the direction of the rounding versus Koko Eating Bananas: there you
*ceil* because a partial pile still costs a whole hour; here you *floor*
because a partial trip earns nothing. Same family, opposite rounding, and
mixing them up is a one-character bug that survives the samples.

Bounds:

- **low = 1.** Time zero completes nothing.
- **high = min(time) · totalTrips.** The fastest bus alone can finish every
  trip in that long, so the answer is never larger.

Do not write `high = 10¹⁴` from the constraints and call it done — the product
bound is the same order of magnitude, but stating it shows you know why the
range is finite. It is also the only bound that stays tight if the constraints
change.
""",
        ),
        (
            "Scale and overflow",
            """
With `time[i]` and `totalTrips` both up to 10⁷, `high` reaches 10¹⁴. That is
the number that kills every simulation-flavoured approach:

- **Tick one unit of time at a time** — 10¹⁴ iterations. Not slow, impossible.
- **Min-heap of "next completion time", pop `totalTrips` times** — 10⁷ pops at
  log n each. Correct, and it also gives you *which* bus made each trip, but it
  is 10⁸-ish operations against binary search's `n · 47`.

The binary search does about 47 halvings of a 10¹⁴ range, each a linear sweep
over at most 10⁵ buses.

10¹⁴ also overflows a 32-bit int by four orders of magnitude, so in C++/Java
`high`, `mid` and the running sum must all be `long long`. The sum needs it
most: with `t = 10¹⁴` and `time[i] = 1`, a single term is already 10¹⁴, and
summing across buses can be capped by early-exiting once the count reaches
`totalTrips`.
""",
        ),
    ],
}


def minimum_time(time: list[int], total_trips: int) -> int:
    def trips_by(deadline: int) -> int:
        return sum(deadline // duration for duration in time)  # floor: partial trips do not count

    low, high = 1, min(time) * total_trips  # the fastest bus alone could do it all
    while low < high:
        mid = (low + high) // 2
        if trips_by(mid) >= total_trips:
            high = mid  # enough; try finishing earlier
        else:
            low = mid + 1

    return low


CASES = [
    (([1, 2, 3], 5), 3),
    (([2], 1), 2),
    (([5, 10, 10], 9), 25),
    (([7, 3, 5], 1), 3),
    (([1, 2, 3], 1), 1),
    (([10, 10], 3), 20),
    (([1], 10000000), 10000000),
]


def solve(time: list[int], total_trips: int) -> int:
    return minimum_time(time, total_trips)
