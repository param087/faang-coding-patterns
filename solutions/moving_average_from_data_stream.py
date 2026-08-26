"""Moving Average from Data Stream — LeetCode 346."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "design",
    "symbol": "MovingAverage",
    "insight": "Keep a running sum, not the window's values: add the arrival, subtract whatever fell off the back.",
    "time": "O(1) per call",
    "space": "O(size)",
    "sections": [
        (
            "What it asks",
            """
Premium, so in my own words: construct the object with a window size, then each
call to `next(value)` returns the mean of the **last `size` values seen**,
including this one. Before `size` values have arrived, average over however many
there are.

Ask whether the window is by count or by time — this one is by count, but the
time-windowed variant ("mean of the last 5 minutes") is the natural follow-up
and needs timestamps and eviction rather than a fixed-length deque. Also ask
whether values are integers; they are on LeetCode, which makes the running sum
exact.
""",
        ),
        (
            "The insight",
            """
The naive `sum(window) / len(window)` is O(size) per call. With `size = 1000`
and 10⁴ calls that is 10⁷ additions to compute numbers that each differ from
the last by two terms.

Keep the sum as state. Exactly one value enters and at most one leaves:

```
total += value
if len(window) > size: total -= window.popleft()
```

`deque` is the right container because the eviction is from the **front** while
the append is at the back — `list.pop(0)` is O(n) and turns an O(1) design into
an O(n) one for no reason. The alternative is a fixed **circular buffer**: a
list of length `size` with an index that wraps, which is what you would
actually write in C and is worth mentioning as the allocation-free version.

Emit the sum divided by `len(window)`, not by `size`, so the warm-up period is
correct without a branch.
""",
        ),
        (
            "Edge cases and the drift nobody mentions",
            """
- **The warm-up.** Fewer than `size` values means dividing by the count so far.
  `next(3)` on a window of 3 returns 3.0, not 1.0.
- **`size = 1`** must return the value itself every time.
- **Negative values** are fine — the running sum handles them, but they are the
  case that catches an implementation that tracks a max or does anything
  clever.
- **Floating-point drift is real** if the stream is floats. Repeatedly adding
  and subtracting accumulates error that never washes out, and a window that
  should read 0.0 can drift to 1e-13. Fixes: keep an integer sum where you can,
  recompute from the window every few thousand updates, or use `math.fsum` over
  the window when exactness matters more than the constant factor.
- **Time-windowed variant**: store `(timestamp, value)` pairs and pop from the
  front while `front_timestamp <= now - window`; the sum bookkeeping is
  identical, only the eviction test changes.
""",
        ),
    ],
}


class MovingAverage:
    def __init__(self, size: int) -> None:
        self.size = size
        self.window: deque[int] = deque()
        self.total = 0  # running sum: never re-add the whole window

    def next(self, val: int) -> float:
        self.window.append(val)
        self.total += val
        if len(self.window) > self.size:
            self.total -= self.window.popleft()  # popleft, not list.pop(0)
        return self.total / len(self.window)  # divide by the count so far


def check() -> None:
    average = MovingAverage(3)
    assert average.next(1) == 1.0  # warm-up: divide by 1
    assert average.next(10) == 5.5
    assert average.next(3) == 14 / 3
    assert average.next(5) == 6.0  # 1 falls off: (10 + 3 + 5) / 3

    unit = MovingAverage(1)
    assert unit.next(4) == 4.0
    assert unit.next(-4) == -4.0
    assert unit.next(0) == 0.0

    signed = MovingAverage(2)
    assert signed.next(-5) == -5.0
    assert signed.next(5) == 0.0
    assert signed.next(-5) == 0.0
    assert signed.next(-5) == -5.0

    # The running sum must stay in step with the window over a long stream.
    long_run = MovingAverage(4)
    values = [7, -3, 0, 12, 5, 5, -20, 1, 1, 1, 1, 100]
    for index, value in enumerate(values):
        expected = values[max(0, index - 3) : index + 1]
        assert long_run.next(value) == sum(expected) / len(expected)
    assert long_run.total == sum(values[-4:])
    assert len(long_run.window) == 4

    # A window larger than the stream never evicts.
    wide = MovingAverage(100)
    assert wide.next(2) == 2.0
    assert wide.next(4) == 3.0
    assert len(wide.window) == 2
