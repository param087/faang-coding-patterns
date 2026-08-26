"""My Calendar II — LeetCode 731."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "intervals",
    "symbol": "MyCalendarTwo",
    "insight": "Keep the double-booked ranges as intervals of their own; a triple booking is exactly an overlap with one of those.",
    "time": "O(n) per booking, O(n²) overall",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`book(start, end)` accepts a half-open interval `[start, end)` unless adding it
would cause a **triple** booking. Double booking is allowed. Return whether it
was accepted, and a rejected booking must leave no trace.

Ask: is `[10,20)` in conflict with `[20,30)`? (No — half-open, so touching is
free, and this is the `<` versus `<=` decision.) How many bookings? (10³ on
LeetCode, so O(n²) total is comfortably fast and the pretty solution is not
required.) Does a rejected call still count towards anything (no).
""",
        ),
        (
            "The insight",
            """
Track **two** collections:

- `booked` — every accepted interval.
- `overlaps` — the intersections of pairs of accepted intervals, i.e. the
  ranges that are currently *double* booked.

Then a new interval causes a triple booking **iff it overlaps something in
`overlaps`**. That is the whole idea: you do not need counts, and you do not
need to know which three bookings collide, only that the region already carries
two.

If it clears that test, accept it — and before storing it, intersect it with
every interval in `booked` and add each non-empty intersection to `overlaps`,
because those regions have just become double booked.

Order matters: the rejection check runs **first and mutates nothing**, so a
refused booking leaves the structure untouched. Interleaving the two loops is
the bug that passes the sample and corrupts state on the first rejection.
""",
        ),
        (
            "The sweep version, and when to reach for it",
            """
The two-list solution does not generalise: "reject the k-th booking" would need
k − 1 lists. The version that does generalise is a **boundary-delta map** —
`+1` at each start, `−1` at each end, then a running prefix sum over the sorted
keys, rejecting if the peak would exceed k − 1.

```
delta[start] += 1; delta[end] -= 1
running = 0
for key in sorted(delta):
    running += delta[key]
    if running > 2: roll the two deltas back and return False
```

Same O(n log n) per call, one parameter instead of a new data structure, and it
is exactly the machinery [My Calendar III](../my-calendar-iii/) needs. Both
versions are below and the tests assert they agree.

The rollback on rejection is the part people forget — you have already written
into the map before you know the answer.
""",
        ),
    ],
}


class MyCalendarTwo:
    def __init__(self) -> None:
        self.booked: list[tuple[int, int]] = []
        self.overlaps: list[tuple[int, int]] = []  # the double-booked ranges

    def book(self, start: int, end: int) -> bool:
        # Overlapping an already double-booked range means a triple booking.
        # This loop runs first and mutates nothing: a rejection leaves no trace.
        for other_start, other_end in self.overlaps:
            if start < other_end and other_start < end:
                return False

        # Accepted: every intersection with an existing booking is now double booked.
        for other_start, other_end in self.booked:
            if start < other_end and other_start < end:
                self.overlaps.append((max(start, other_start), min(end, other_end)))

        self.booked.append((start, end))
        return True


class MyCalendarTwoSweep:
    """Boundary deltas — the version that generalises to a k-booking limit."""

    def __init__(self, limit: int = 2) -> None:
        self.limit = limit
        self.delta: dict[int, int] = defaultdict(int)

    def book(self, start: int, end: int) -> bool:
        self.delta[start] += 1
        self.delta[end] -= 1

        running = 0
        for key in sorted(self.delta):
            running += self.delta[key]
            if running > self.limit:
                self.delta[start] -= 1  # roll back: the booking never happened
                self.delta[end] += 1
                return False

        return True


def check() -> None:
    scripts = [
        # LeetCode's own sequence.
        ([(10, 20), (50, 60), (10, 40), (5, 15), (5, 10), (25, 55)],
         [True, True, True, False, True, True]),
        # Touching is never a conflict, however many times it happens.
        ([(10, 20), (20, 30), (30, 40), (10, 20), (20, 30)],
         [True, True, True, True, True]),
        # A third booking of the same range is refused; the first two are not.
        ([(10, 20), (10, 20), (10, 20), (15, 16)],
         [True, True, False, False]),
        # Containment in both directions.
        ([(1, 100), (20, 30), (25, 26), (99, 200)],
         [True, True, False, True]),
        # A rejection must not poison later bookings.
        ([(0, 10), (0, 10), (0, 10), (10, 20), (10, 20)],
         [True, True, False, True, True]),
    ]

    for operations, expected in scripts:
        calendar = MyCalendarTwo()
        sweep = MyCalendarTwoSweep()
        assert [calendar.book(*op) for op in operations] == expected
        assert [sweep.book(*op) for op in operations] == expected  # both agree

        # Only the accepted bookings were stored.
        assert len(calendar.booked) == sum(expected)
