"""Stock Price Fluctuation — LeetCode 2034."""

from __future__ import annotations

from heapq import heappop, heappush

META = {
    "pattern": "design",
    "symbol": "StockPrice",
    "insight": "The timestamp-to-price map is the only truth; the heaps are indexes that may lie, so validate a top against the map before trusting it.",
    "time": "O(log n) update, O(1) current, O(log n) amortised maximum and minimum",
    "space": "O(number of updates)",
    "sections": [
        (
            "What it asks",
            """
A stream of `update(timestamp, price)` records where a timestamp may arrive
**again** with a corrected price, and where records may arrive **out of
order**. Support `current()` — the price at the latest timestamp seen —
plus `maximum()` and `minimum()` over the corrected view of the data.

The clarifying question that matters: **does `current()` mean the most recent
call, or the largest timestamp?** The largest timestamp. A correction to an old
record must not change `current()`, and a record that arrives late must not
either. Also confirm that a correction replaces the price rather than adding a
second record at the same instant.
""",
        ),
        (
            "The insight",
            """
Corrections are what makes this more than a running max. A `SortedList` of
prices would work — remove the old price, insert the new one, both O(log n) —
and if the interviewer allows the library, say so, because it is the shortest
correct answer.

Without it: keep `dict[timestamp] -> price` as the **source of truth**, plus a
min-heap and a max-heap of `(price, timestamp)` pairs as indexes. `update`
writes the map and pushes to both heaps without removing anything, because a
binary heap cannot delete an interior element.

That leaves stale pairs in the heaps, so the heaps are treated as *hints*:
before reading a top, check it against the map, and discard it while
`prices[timestamp] != price`. This is **lazy deletion**, and the invariant that
makes it sound is one line — a pair is valid exactly when the map still agrees
with it, and validity is monotone: once a timestamp is corrected away from a
price, that pair can never become valid again.

`current()` needs no heap at all. Track the maximum timestamp seen and read the
map: O(1).
""",
        ),
        (
            "Where the heaps lie",
            """
Take `update(1, 10)`, `update(2, 5)`, then the correction `update(1, 3)`.

The max-heap top is `(-10, 1)`, but the map now says timestamp 1 holds 3. The
validation check catches the mismatch, discards the pair, and the next top is
`(-5, 2)` — the correct answer, **5**. Skip the check and the structure reports
a maximum of 10 forever, from a price that was retracted.

Three details worth stating:

- **Both heaps must be validated**, not just the one you think went stale. A
  correction upward makes the min-heap entry wrong; a correction downward makes
  the max-heap entry wrong. Which one breaks depends on the data.
- **Validate lazily, never eagerly.** Purging on `update` would require finding
  an arbitrary element in a heap, which is the O(n) operation you are avoiding.
- **Memory grows with updates, not with distinct timestamps.** Bounded at
  10⁵ here so it is a non-issue; in a long-lived process you would rebuild the
  heaps once the dead fraction gets large, or use a `SortedList`.
""",
        ),
    ],
}


class StockPrice:
    def __init__(self) -> None:
        self.prices: dict[int, int] = {}  # the source of truth
        self.latest = 0
        self.max_heap: list[tuple[int, int]] = []  # (-price, timestamp)
        self.min_heap: list[tuple[int, int]] = []  # (price, timestamp)

    def update(self, timestamp: int, price: int) -> None:
        self.prices[timestamp] = price  # a correction overwrites
        self.latest = max(self.latest, timestamp)  # late arrivals must not win
        heappush(self.max_heap, (-price, timestamp))
        heappush(self.min_heap, (price, timestamp))

    def current(self) -> int:
        return self.prices[self.latest]

    def maximum(self) -> int:
        # Discard pairs the map no longer agrees with.
        while self.prices[self.max_heap[0][1]] != -self.max_heap[0][0]:
            heappop(self.max_heap)
        return -self.max_heap[0][0]

    def minimum(self) -> int:
        while self.prices[self.min_heap[0][1]] != self.min_heap[0][0]:
            heappop(self.min_heap)
        return self.min_heap[0][0]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    stock = StockPrice()
    stock.update(1, 10)
    stock.update(2, 5)
    assert stock.current() == 5
    assert stock.maximum() == 10
    stock.update(1, 3)  # correction: 10 was wrong
    assert stock.maximum() == 5  # not 10
    assert stock.minimum() == 3
    stock.update(4, 2)
    assert stock.current() == 2
    assert stock.minimum() == 2

    # A single record is simultaneously the current, the max and the min.
    single = StockPrice()
    single.update(7, 42)
    assert single.current() == 42
    assert single.maximum() == 42
    assert single.minimum() == 42

    # Out-of-order arrival: current() follows the timestamp, not the call.
    late = StockPrice()
    late.update(10, 100)
    late.update(3, 1)  # arrives late, is older
    assert late.current() == 100
    assert late.minimum() == 1
    assert late.maximum() == 100
    late.update(11, 50)
    assert late.current() == 50

    # Correcting the latest timestamp changes current() too.
    corrected = StockPrice()
    corrected.update(5, 20)
    corrected.update(5, 25)
    assert corrected.current() == 25
    assert corrected.maximum() == 25
    assert corrected.minimum() == 25  # the 20 pair is stale in both heaps

    # A correction upward is the case that breaks the min-heap only.
    upward = StockPrice()
    upward.update(1, 1)
    upward.update(2, 8)
    assert upward.minimum() == 1
    upward.update(1, 9)
    assert upward.minimum() == 8
    assert upward.maximum() == 9

    # Repeated corrections to the same timestamp leave a trail of dead pairs.
    churn = StockPrice()
    churn.update(1, 5)
    for price in range(6, 30):
        churn.update(1, price)
    churn.update(2, 7)
    assert churn.current() == 7
    assert churn.maximum() == 29
    assert churn.minimum() == 7
    churn.update(1, 1)
    assert churn.maximum() == 7
    assert churn.minimum() == 1
