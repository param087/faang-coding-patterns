"""Logger Rate Limiter — LeetCode 359."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "design",
    "symbol": "Logger",
    "insight": "One map of message → next allowed timestamp answers it; the real question is how you stop that map growing forever.",
    "time": "O(1) amortised per call",
    "space": "O(distinct messages), or O(messages seen in the last window) if you evict",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so in my own words: you are given a `Logger` with a single
method taking a timestamp in seconds and a message string. It returns whether
the message may be printed. A message may print at most **once every 10
seconds**; calls arrive in **non-decreasing** timestamp order, possibly several
at the same second.

Two clarifications decide the code. **Is the window inclusive?** A message
printed at t = 1 is allowed again at exactly t = 11, not t = 12 — so the test
is `timestamp >= allowed_at`, and getting that boundary backwards is the
single most common way to fail this. **Are timestamps guaranteed
non-decreasing?** Yes, and that guarantee is what makes eviction cheap; without
it you would need to keep history rather than a single "next allowed" per
message.
""",
        ),
        (
            "The insight",
            """
Do not store a window of events. Store, per message, the **one timestamp at
which it becomes printable again**:

```
if timestamp >= allowed_at.get(message, 0):
    allowed_at[message] = timestamp + 10
    return True
return False
```

Note the asymmetry that people get wrong: the map is updated **only on a
successful print**. A rejected call must not push the deadline out, or a
message hammered every second is suppressed forever — a rate limiter that
starves the very traffic it is meant to sample.

Default of `0` rather than `-inf` works because timestamps start at 1 in the
stated constraints; if 0 were a legal timestamp, use `-10` or a membership
test.
""",
        ),
        (
            "The memory problem, which is the actual interview",
            """
The three-line version never forgets a message. A logger running for a day over
a million distinct messages holds a million entries to answer questions about
the last 10 seconds. State the leak before the interviewer does.

Two fixes worth naming:

- **Lazy eviction with a queue.** Since timestamps are non-decreasing, push
  `(timestamp, message)` on a deque when you print and pop from the front while
  `front_timestamp + 10 <= now`, deleting those map entries. Memory becomes
  O(messages in the last 10 seconds); each message is pushed and popped once,
  so it is still O(1) amortised. `EvictingLogger` below does this.
- **Two rotating maps** (the standard sliding-window-counter trick): a current
  and a previous bucket, swapped every 10 seconds, so the old bucket is dropped
  wholesale rather than key by key. Constant memory bound, one extra lookup.

Follow-ups that follow naturally: multithreading (shard the map by
`hash(message)` and lock per shard, so hot messages do not serialise everything);
distributed limiting (Redis with `SET key NX PX 10000`, which is exactly this
algorithm with a TTL doing the eviction); and moving from "once per 10s" to
"N per 10s", which is a token bucket rather than a single deadline.
""",
        ),
    ],
}


class Logger:
    """The interview answer: one map from message to its next allowed timestamp."""

    def __init__(self, window: int = 10) -> None:
        self.window = window
        self.allowed_at: dict[str, int] = {}

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        if timestamp >= self.allowed_at.get(message, 0):
            self.allowed_at[message] = timestamp + self.window  # only on success
            return True
        return False


class EvictingLogger:
    """Same answer, but memory is bounded by the last `window` seconds of traffic."""

    def __init__(self, window: int = 10) -> None:
        self.window = window
        self.allowed_at: dict[str, int] = {}
        self.printed: deque[tuple[int, str]] = deque()  # (printed_at, message)

    def _evict(self, now: int) -> None:
        # Timestamps are non-decreasing, so the front of the queue is the oldest.
        while self.printed and self.printed[0][0] + self.window <= now:
            printed_at, message = self.printed.popleft()
            if self.allowed_at.get(message) == printed_at + self.window:
                del self.allowed_at[message]

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        self._evict(timestamp)
        if timestamp >= self.allowed_at.get(message, 0):
            self.allowed_at[message] = timestamp + self.window
            self.printed.append((timestamp, message))
            return True
        return False


def check() -> None:
    for factory in (Logger, EvictingLogger):
        logger = factory()
        assert logger.shouldPrintMessage(1, "foo") is True
        assert logger.shouldPrintMessage(2, "bar") is True
        assert logger.shouldPrintMessage(3, "foo") is False
        assert logger.shouldPrintMessage(8, "bar") is False
        assert logger.shouldPrintMessage(10, "foo") is False  # 10 < 1 + 10
        assert logger.shouldPrintMessage(11, "foo") is True  # boundary is inclusive

        # A rejected call must not extend the deadline.
        greedy = factory()
        assert greedy.shouldPrintMessage(1, "spam") is True
        for second in range(2, 11):
            assert greedy.shouldPrintMessage(second, "spam") is False
        assert greedy.shouldPrintMessage(11, "spam") is True

        # Distinct messages are independent, and same-second repeats are rejected.
        multi = factory()
        assert multi.shouldPrintMessage(5, "a") is True
        assert multi.shouldPrintMessage(5, "b") is True
        assert multi.shouldPrintMessage(5, "a") is False

        # A long gap: everything is printable again.
        stale = factory()
        assert stale.shouldPrintMessage(1, "x") is True
        assert stale.shouldPrintMessage(1_000_000, "x") is True

    # The evicting variant must actually shed state, not just answer correctly.
    evicting = EvictingLogger()
    for second in range(1, 101):
        evicting.shouldPrintMessage(second, f"msg-{second}")
    assert len(evicting.allowed_at) <= 10
    assert len(evicting.printed) <= 10
