"""My Calendar I — LeetCode 729."""

from __future__ import annotations

from bisect import bisect_right

META = {
    "pattern": "ordered-set",
    "symbol": "MyCalendar",
    "insight": "A new booking can only conflict with its immediate neighbours in sorted order — two lookups, not a scan.",
    "time": "O(log n) search, O(n) insert with a list",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`book(start, end)` adds a half-open interval `[start, end)` unless it overlaps
an existing booking, in which case it is rejected.

Ask: **does `[10,20)` conflict with `[20,30)`?** (No — touching is fine, and
this is the question that decides `<` versus `<=`.) How many bookings? (10³,
so an O(n) insert is perfectly acceptable.) Must a rejected booking leave no
trace?
""",
        ),
        (
            "The naive answer passes",
            """
Check the new interval against every existing one: O(n) per booking, O(n²)
overall. At n = 1000 that is 10⁶ — **it passes.**

Say so, then improve it anyway, because the improvement is the point of the
question and because the O(n²) version does not scale to My Calendar II or
III.
""",
        ),
        (
            "The insight",
            """
Keep bookings sorted by start. Then a new booking can only conflict with its
**immediate neighbours**:

- The booking starting just *before* us must **end** by the time we start.
- The booking starting just *after* us must **start** at or after we end.

Two lookups settle it. Nothing else can possibly overlap, because everything
earlier ends before the neighbour does and everything later starts after it.

Thinking in terms of neighbours also avoids enumerating the four overlap cases
naively — there are only two conditions here, not four.
""",
        ),
        (
            "The Python problem, stated",
            """
This is really an ordered-set problem, and **Python has no ordered set in the
standard library**.

`bisect` on a plain list gives O(log n) search but **O(n) insert**, because the
list shifts. That is fine at n = 1000 and quadratic beyond.

Say it explicitly:

> "I'd use `SortedList` from `sortedcontainers` — it isn't standard library, so
> if that's unavailable I'll use `bisect` on a list and accept O(n) insertion,
> which is fine at this n."

Claiming O(log n) for `insort` is the thing to avoid.
""",
        ),
        (
            "Dry run",
            """
```
book(10, 20)  -> True
book(15, 25)  -> False   starts inside the first
book(20, 30)  -> True    touching is not overlapping
book(5, 10)   -> True    ends exactly where the first begins
book(8, 12)   -> False   straddles the boundary
```

The third and fourth cases are what test your `<`.
""",
        ),
        (
            "Follow-ups",
            """
- **My Calendar II** — allow double booking, reject triple. Track a second list
  of known overlaps, or sweep a boundary-count map.
- **My Calendar III** — report the maximum overlap at any time. That is a
  [segment tree with lazy propagation](../../patterns/segment-tree/), or a
  sorted boundary-delta map.

The three make a ladder, and interviewers walk up it.
""",
        ),
    ],
}


class MyCalendar:
    def __init__(self) -> None:
        self.starts: list[int] = []
        self.ends: list[int] = []

    def book(self, start: int, end: int) -> bool:
        index = bisect_right(self.starts, start)

        # The booking starting just before us must finish by the time we start.
        if index > 0 and self.ends[index - 1] > start:
            return False
        # The booking starting just after us must begin at or after our end.
        if index < len(self.starts) and self.starts[index] < end:
            return False

        # O(n) insert: bisect finds the position in O(log n), the shift is O(n).
        self.starts.insert(index, start)
        self.ends.insert(index, end)
        return True


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    calendar = MyCalendar()
    assert calendar.book(10, 20) is True
    assert calendar.book(15, 25) is False  # starts inside the first
    assert calendar.book(20, 30) is True  # touching is not overlapping
    assert calendar.book(5, 10) is True  # ends exactly where the first begins
    assert calendar.book(8, 12) is False  # straddles a boundary

    # A rejected booking must leave no trace.
    assert len(calendar.starts) == 3

    # Containment, both directions.
    nested = MyCalendar()
    assert nested.book(10, 50) is True
    assert nested.book(20, 30) is False  # fully inside
    assert nested.book(5, 60) is False  # fully contains

    # Insertion order must not matter.
    shuffled = MyCalendar()
    for start, end in ((40, 50), (10, 20), (25, 35)):
        assert shuffled.book(start, end) is True
    assert shuffled.starts == [10, 25, 40]
    assert shuffled.book(30, 45) is False
