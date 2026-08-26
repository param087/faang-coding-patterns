"""Design Authentication Manager — LeetCode 1797."""

from __future__ import annotations

from collections import OrderedDict

META = {
    "pattern": "design",
    "symbol": "AuthenticationManager",
    "insight": "Call times only increase, so every generate and renew mints the newest expiry — an ordered map stays sorted and counting is O(1).",
    "time": "O(1) amortised per operation",
    "space": "O(live tokens)",
    "sections": [
        (
            "What it asks",
            """
Tokens with a fixed time-to-live. `generate(token, now)` issues a token that
expires at `now + ttl`. `renew(token, now)` pushes the expiry to `now + ttl`,
but **only if the token exists and has not already expired** — otherwise it is
silently ignored. `count_unexpired_tokens(now)` returns how many are still
alive. Every call arrives with a strictly larger `now` than the last.

Ask the only question that decides correctness: **is a token expiring exactly
at `now` alive or dead?** Dead. Expiry is at the *start* of second
`now + ttl`, so the test is `expiry > now`, not `>=`.
""",
        ),
        (
            "The insight",
            """
A plain `dict[token] -> expiry` is already correct, with counting done by
scanning the values: O(1) writes, O(n) counts, and at 2000 calls that passes.
Write it if you are short on time and say what it costs.

The better answer comes from the guarantee that call times **strictly
increase**. Follow the consequence: any token touched now gets expiry
`now + ttl`, and every token touched earlier got a strictly smaller expiry. So
if you move each token to the back of an `OrderedDict` whenever it is generated
or renewed, **the map is permanently sorted by expiry** — for free, with no
comparisons and no heap.

Sorted by expiry means the expired tokens are always a **prefix**. Pop from the
front while the head has expired, and every operation becomes amortised O(1):
each token is inserted once and evicted once. `count_unexpired_tokens` is then
`len(...)`, and — this is the part worth noticing — the same purge keeps
`renew` honest for free, because an expired token is no longer in the map to
be renewed.

Notice what is *not* here: no heap, no sorting, no expiry timer thread. The
input ordering did that work.
""",
        ),
        (
            "The boundary that decides it",
            """
Run the canonical trace with `ttl = 5`:

```
renew("aaa", 1)               no such token -> ignored
generate("aaa", 2)            expires at 7
count_unexpired_tokens(6)     -> 1
generate("bbb", 7)            expires at 12
renew("aaa", 8)               expired at 7 -> ignored, NOT resurrected
renew("bbb", 10)              alive -> expires at 15
count_unexpired_tokens(15)    -> 0
```

Two lines carry the whole problem. `renew("aaa", 8)` must not recreate a dead
token — an implementation that assigns `expiry[token] = now + ttl` without
checking membership brings it back from the dead. And the final count is
**0, not 1**: "bbb" expires at exactly 15, and expiry at `now` means gone.

The off-by-one appears in three places — the purge condition, the `renew`
liveness test, and the count — so define the predicate once (`expiry > now`) and
reuse it. Deriving all three separately is how one of them ends up `>=`.
""",
        ),
    ],
}


class AuthenticationManager:
    def __init__(self, time_to_live: int) -> None:
        self.ttl = time_to_live
        # Insertion order == expiry order, because call times only increase.
        self.expiry: OrderedDict[str, int] = OrderedDict()

    def _purge(self, current_time: int) -> None:
        # Expired tokens are always a prefix, so stop at the first live one.
        while self.expiry and next(iter(self.expiry.values())) <= current_time:
            self.expiry.popitem(last=False)

    def generate(self, token_id: str, current_time: int) -> None:
        self._purge(current_time)
        self.expiry[token_id] = current_time + self.ttl
        self.expiry.move_to_end(token_id)  # newest expiry goes to the back

    def renew(self, token_id: str, current_time: int) -> None:
        self._purge(current_time)
        if token_id not in self.expiry:
            return  # unknown or already expired: never resurrect it
        self.expiry[token_id] = current_time + self.ttl
        self.expiry.move_to_end(token_id)

    def count_unexpired_tokens(self, current_time: int) -> int:
        self._purge(current_time)
        return len(self.expiry)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    manager = AuthenticationManager(5)
    manager.renew("aaa", 1)  # no such token, ignored
    manager.generate("aaa", 2)  # expires at 7
    assert manager.count_unexpired_tokens(6) == 1
    manager.generate("bbb", 7)  # expires at 12
    manager.renew("aaa", 8)  # already expired at 7, must stay dead
    manager.renew("bbb", 10)  # alive, now expires at 15
    assert manager.count_unexpired_tokens(15) == 0  # expiry at now means gone

    # The boundary, isolated: alive at ttl - 1 past issue, dead at ttl.
    edge = AuthenticationManager(5)
    edge.generate("t", 1)  # expires at 6
    assert edge.count_unexpired_tokens(5) == 1
    assert edge.count_unexpired_tokens(6) == 0

    # Renewal at the last live instant extends the token.
    renewed = AuthenticationManager(5)
    renewed.generate("t", 1)  # expires at 6
    renewed.renew("t", 5)  # still alive at 5, now expires at 10
    assert renewed.count_unexpired_tokens(9) == 1
    assert renewed.count_unexpired_tokens(10) == 0

    # Renewing at the exact expiry instant is a no-op, not an extension.
    expired = AuthenticationManager(5)
    expired.generate("t", 1)  # expires at 6
    expired.renew("t", 6)  # dead at 6
    assert expired.count_unexpired_tokens(7) == 0

    # Many tokens expiring in waves; the front prefix is what drains.
    waves = AuthenticationManager(10)
    for step in range(5):
        waves.generate(f"t{step}", step)  # expiries 10, 11, 12, 13, 14
    assert waves.count_unexpired_tokens(9) == 5
    assert waves.count_unexpired_tokens(11) == 3  # t0 and t1 are gone
    waves.renew("t4", 12)  # t2 expires at 12 and is purged; t4 moves to 22
    assert waves.count_unexpired_tokens(12) == 2  # t3 and t4 remain
    assert waves.count_unexpired_tokens(13) == 1  # t3 expires at exactly 13
    assert waves.count_unexpired_tokens(21) == 1
    assert waves.count_unexpired_tokens(22) == 0

    # Insertion order must track expiry order after a renewal, not push order.
    ordering = AuthenticationManager(100)
    ordering.generate("old", 1)  # expires at 101
    ordering.generate("new", 2)  # expires at 102
    ordering.renew("old", 3)  # expires at 103, moves behind "new"
    assert list(ordering.expiry.items()) == [("new", 102), ("old", 103)]
    assert ordering.count_unexpired_tokens(102) == 1
    assert ordering.count_unexpired_tokens(103) == 0

    # A token generated with an id that expired earlier is a fresh token.
    reissued = AuthenticationManager(2)
    reissued.generate("t", 1)  # expires at 3
    assert reissued.count_unexpired_tokens(3) == 0
    reissued.generate("t", 4)  # expires at 6
    assert reissued.count_unexpired_tokens(5) == 1
