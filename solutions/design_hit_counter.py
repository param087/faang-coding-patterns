"""Design Hit Counter — LeetCode 362."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "design",
    "symbol": "HitCounter",
    "insight": "Timestamps only move forwards, so what leaves the 300-second window never returns — evict from the front, keep a running total.",
    "time": "O(1) amortised per call",
    "space": "O(distinct seconds in the window), at most 300 entries",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so the statement is not public — in my own words: a
counter with `hit(timestamp)` recording one hit at that second and
`get_hits(timestamp)` returning how many hits fell in the **past 5 minutes**,
meaning the 300 seconds ending at that timestamp. Timestamps are in seconds and
arrive in non-decreasing order across calls.

Two questions decide the whole design. **Is the window inclusive at both ends?**
A hit at second `t - 300` is already out; `t - 299` is still in. And **are
timestamps guaranteed monotonic?** They are, and that guarantee is what makes a
queue legal instead of a heap.
""",
        ),
        (
            "The insight",
            """
Store hits in a queue ordered by time, and let each call evict from the front
everything older than the window. Because timestamps never go backwards, an
evicted hit can never become relevant again — that is the whole argument, and
it is the argument the interviewer wants to hear.

Two refinements turn the naive version into the real answer:

- **Collapse equal seconds.** Push `[timestamp, count]` pairs and bump the
  count when the newest entry is the same second. Now memory is bounded by the
  number of **distinct seconds** in the window — at most 300 entries — no
  matter whether the service takes 10 hits a second or 10 million.
- **Keep a running total.** Maintain `total` as you push and evict, so
  `get_hits` is O(1) instead of summing the queue. Eviction is amortised O(1):
  every entry is pushed once and popped once.

The alternative you will see is a fixed 300-slot array of `(second, count)`
indexed by `timestamp % 300`, overwriting a slot whose stamp is stale. It is
genuinely O(1) memory, which is the better answer if hits are relentless and
sparse queries are fine — but `get_hits` then scans all 300 slots. Name both
and pick one; the queue generalises to a variable window, the array does not.
""",
        ),
        (
            "Follow-ups",
            """
- **"Hits arrive out of order."** The queue argument collapses immediately.
  Bucket by second in a hash map and keep the window with a heap, or accept an
  approximation — and push back that in a real system late events are usually
  handled by watermarks, not by a data structure.
- **"Many threads."** The pair-with-count layout is friendly: shard by thread,
  each shard keeping its own deque, and sum the shards on read. A single lock
  around `hit` would serialise the hottest path in the service.
- **"A 24-hour window, per user."** 86,400 entries per user is too much state.
  This is where you switch to fixed buckets — per-minute counters with a
  partial bucket at each edge, which is exactly how rate limiters are built.
- **Sliding window rate limiting** is the same question wearing a different
  hat: `hit` returns whether the count is still under a limit.
""",
        ),
    ],
}

WINDOW = 300  # seconds; "the past 5 minutes"


class HitCounter:
    def __init__(self) -> None:
        # [second, count] pairs, seconds strictly increasing.
        self.hits: deque[list[int]] = deque()
        self.total = 0

    def _evict(self, timestamp: int) -> None:
        # A hit at second h counts while h > timestamp - WINDOW.
        while self.hits and self.hits[0][0] <= timestamp - WINDOW:
            self.total -= self.hits.popleft()[1]

    def hit(self, timestamp: int) -> None:
        self._evict(timestamp)
        if self.hits and self.hits[-1][0] == timestamp:
            self.hits[-1][1] += 1  # same second: bump, do not append
        else:
            self.hits.append([timestamp, 1])
        self.total += 1

    def get_hits(self, timestamp: int) -> int:
        self._evict(timestamp)
        return self.total


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    counter = HitCounter()
    assert counter.get_hits(1) == 0  # nothing recorded yet
    counter.hit(1)
    counter.hit(2)
    counter.hit(3)
    assert counter.get_hits(4) == 3
    counter.hit(300)
    assert counter.get_hits(300) == 4  # second 1 is still inside the window
    assert counter.get_hits(301) == 3  # and now it is exactly 300 old, so out
    assert counter.get_hits(302) == 2

    # The boundary, isolated: a hit at t survives until t + 299.
    boundary = HitCounter()
    boundary.hit(1)
    assert boundary.get_hits(300) == 1
    assert boundary.get_hits(301) == 0

    # Thousands of hits in one second collapse into a single queue entry.
    burst = HitCounter()
    for _ in range(5000):
        burst.hit(10)
    assert burst.get_hits(10) == 5000
    assert len(burst.hits) == 1
    assert burst.get_hits(309) == 5000
    assert burst.get_hits(310) == 0

    # A long silence flushes everything, and the counter still works after.
    gap = HitCounter()
    for second in range(1, 51):
        gap.hit(second)
    assert gap.get_hits(50) == 50
    assert gap.get_hits(100_000) == 0
    gap.hit(100_000)
    assert gap.get_hits(100_000) == 1
    assert len(gap.hits) == 1  # eviction reclaims the old entries

    # Repeated hits on the same second interleaved with new seconds.
    mixed = HitCounter()
    for second in (5, 5, 5, 6, 7, 7):
        mixed.hit(second)
    assert mixed.get_hits(7) == 6
    assert len(mixed.hits) == 3
    assert mixed.get_hits(305) == 3  # seconds 5 dropped, 6 and 7 remain
    assert mixed.get_hits(306) == 2
