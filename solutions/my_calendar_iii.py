"""My Calendar III — LeetCode 732."""

from __future__ import annotations

from bisect import insort
from collections import defaultdict

META = {
    "pattern": "intervals",
    "symbol": "MyCalendarThree",
    "insight": "Store only the boundaries: +1 at each start, −1 at each end, and the largest running sum is the deepest overlap.",
    "time": "O(n log n) per booking, O(n² log n) overall",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`book(start, end)` always succeeds. After each call, return **k** — the largest
number of half-open intervals `[start, end)` that overlap at any single point.

Ask: is a booking ever rejected? (No — that is the whole difference from
[My Calendar II](../my-calendar-ii/), and it removes the rollback problem.)
Half-open, so does `[10,20)` overlapping `[20,30)` count as 2? (No — 1.) How
many calls? (400 on LeetCode, which is the licence for the O(n²) sweep below.)
""",
        ),
        (
            "The insight",
            """
Never store intervals. Store the **boundaries where the count changes**: `+1`
at every start, `−1` at every end, in a map keyed by coordinate. Walk the keys
in sorted order accumulating a running total and the running total *is* the
number of live bookings on the segment starting at that key. The maximum over
all keys is the answer.

The half-open semantics come out for free, and this is the part worth saying
out loud: an end at `x` and a start at `x` land on the **same key** and cancel
before the running total is read, so `[10,20)` and `[20,30)` never register as
2. Under a sweep over a *list* of events you would have to force `−1` to sort
before `+1`; summing into a map removes the tie-break entirely.

Note the counts never decrease across calls, so `max` over the whole map each
time is not wasted work — you could also keep the previous answer and take the
max. Same thing.
""",
        ),
        (
            "Cost, and the version that scales",
            """
Re-sorting the keys on every call is O(n log n) per booking, O(n² log n) for
the sequence. At n = 400 that is roughly 400² · 9 ≈ 1.4 million operations —
milliseconds, so **it passes**, and the code is eight lines.

Say that, then say what you would do if n were 10⁵:

- Keep the boundaries in a sorted structure so each `book` is one insertion
  plus one linear pass: `insort` into a list, or `SortedDict` from
  `sortedcontainers` (not standard library — flag it). Still O(n) per call, but
  no re-sort. That variant is below and the tests assert it agrees.
- The real answer is a **segment tree with lazy propagation** over the
  coordinate range, or a dynamic/implicit one: range-add `+1` on `[start, end)`
  and query the global max, both O(log C) with C = 10⁹. That is what the "Hard"
  tag is for, and naming it matters more than writing all sixty lines of it.

The trap for the naive alternative — keeping a list of intervals and recounting
overlaps pairwise — is that it answers the wrong question: pairwise overlap
counting does not tell you how many are live at one instant.
""",
        ),
    ],
}


class MyCalendarThree:
    def __init__(self) -> None:
        self.delta: dict[int, int] = defaultdict(int)

    def book(self, start: int, end: int) -> int:
        self.delta[start] += 1
        self.delta[end] -= 1  # same key as a start at `end`: they cancel

        running = best = 0
        for key in sorted(self.delta):
            running += self.delta[key]
            best = max(best, running)
        return best


class MyCalendarThreeSorted:
    """Same sweep, keeping the boundaries sorted so no call re-sorts them."""

    def __init__(self) -> None:
        self.keys: list[int] = []
        self.delta: dict[int, int] = defaultdict(int)

    def book(self, start: int, end: int) -> int:
        for point in (start, end):
            if point not in self.delta:
                insort(self.keys, point)  # O(n) shift, O(log n) search
        self.delta[start] += 1
        self.delta[end] -= 1

        running = best = 0
        for key in self.keys:
            running += self.delta[key]
            best = max(best, running)
        return best


def check() -> None:
    scripts = [
        # LeetCode's own sequence.
        ([(10, 20), (50, 60), (10, 40), (5, 15), (5, 10), (25, 55)],
         [1, 1, 2, 3, 3, 3]),
        # Half-open: back-to-back bookings never stack.
        ([(10, 20), (20, 30), (30, 40), (10, 40)],
         [1, 1, 1, 2]),
        # Identical intervals stack exactly.
        ([(0, 10), (0, 10), (0, 10), (0, 10)],
         [1, 2, 3, 4]),
        # Nesting: the innermost point carries all three.
        ([(1, 100), (10, 90), (40, 50), (200, 300)],
         [1, 2, 3, 3]),
        # k never falls back, even when later bookings are disjoint.
        ([(5, 6), (5, 6), (100, 200)],
         [1, 2, 2]),
        # Negative and zero coordinates.
        ([(-10, 0), (-5, 5), (-1, 1)],
         [1, 2, 3]),
    ]

    for operations, expected in scripts:
        calendar = MyCalendarThree()
        sorted_variant = MyCalendarThreeSorted()
        assert [calendar.book(*op) for op in operations] == expected
        assert [sorted_variant.book(*op) for op in operations] == expected
