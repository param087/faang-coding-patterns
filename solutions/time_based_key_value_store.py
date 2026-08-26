"""Time Based Key-Value Store — LeetCode 981."""

from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict

META = {
    "pattern": "design",
    "symbol": "TimeMap",
    "insight": "Timestamps arrive increasing, so each key's list is already sorted — get is a binary search for the largest time not exceeding the query.",
    "time": "O(1) set, O(log n) get",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`set(key, value, timestamp)` and `get(key, timestamp)` returning the value with
the **largest timestamp at or before** the query. Empty string if none exists.

Ask: **are timestamps strictly increasing per key?** (Yes — and this is the
question that makes `set` O(1) rather than requiring an insertion sort.) Can
the same timestamp repeat? What if nothing was set that early?
""",
        ),
        (
            "The insight",
            """
Because timestamps arrive in increasing order, each key's list of versions is
**already sorted** — you never have to sort or insert in the middle.

So `set` is an append, O(1). And `get` is a binary search for the largest
timestamp `<= t`, O(log n) in the number of versions of that key.

Noticing the ordering guarantee is the whole solve; without it this becomes a
much messier problem.
""",
        ),
        (
            "The bound",
            """
`bisect_right(times, timestamp) - 1`.

`bisect_right` gives the first index **strictly greater** than the query, so
one before it is the last index `<= t` — including an exact match, which is
what "at or before" requires.

`bisect_left` would exclude an exact match and return the previous version.
That is an off-by-one that returns the wrong value, and it is exactly what
this problem tests.
""",
        ),
        (
            "The empty case",
            """
If the index lands at −1, nothing was set at or before that time — return the
empty string rather than indexing with −1, which would silently return the
*newest* value.

Python's negative indexing makes this failure mode particularly quiet.
""",
        ),
        (
            "Dry run",
            """
```
set("foo", "bar", 1)
get("foo", 1)  -> "bar"    exact match
get("foo", 3)  -> "bar"    latest at or before 3
set("foo", "bar2", 4)
get("foo", 4)  -> "bar2"
get("foo", 5)  -> "bar2"
get("foo", 0)  -> ""       nothing that early
```

That last one is where the off-by-one shows up.
""",
        ),
        (
            "Follow-ups",
            """
- **Timestamps not increasing** — `set` needs `insort`, which is O(n) per
  insert. Say so.
- **Delete a version, or a range** — the sorted list still works, but removal
  is O(n); an [ordered structure](../../patterns/ordered-set/) is better.
- **Snapshot Array** — the same idea, versioning per index rather than per
  key.
""",
        ),
    ],
}


class TimeMap:
    def __init__(self) -> None:
        # Per key: parallel sorted lists of timestamps and values.
        self.store: dict[str, tuple[list[int], list[str]]] = defaultdict(lambda: ([], []))

    def set(self, key: str, value: str, timestamp: int) -> None:
        times, values = self.store[key]
        times.append(timestamp)  # already sorted: timestamps only increase
        values.append(value)

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ""
        times, values = self.store[key]
        # bisect_right - 1 = the last entry at or before `timestamp`.
        index = bisect_right(times, timestamp) - 1
        return values[index] if index >= 0 else ""


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    times = TimeMap()
    times.set("foo", "bar", 1)
    assert times.get("foo", 1) == "bar"  # exact match must be included
    assert times.get("foo", 3) == "bar"
    times.set("foo", "bar2", 4)
    assert times.get("foo", 4) == "bar2"
    assert times.get("foo", 5) == "bar2"
    assert times.get("foo", 0) == ""  # nothing set that early
    assert times.get("missing", 1) == ""

    many = TimeMap()
    for t in range(1, 11):
        many.set("k", f"v{t}", t * 10)
    assert many.get("k", 55) == "v5"
    assert many.get("k", 100) == "v10"
    assert many.get("k", 9) == ""
