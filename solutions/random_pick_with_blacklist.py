"""Random Pick with Blacklist — LeetCode 710."""

from __future__ import annotations

import random
from collections import Counter

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Draw from [0, m) where m is the number of survivors, and remap the blacklisted values below m onto the survivors above it.",
    "time": "O(b) build, O(1) per pick",
    "space": "O(b)",
    "sections": [
        (
            "What it asks",
            """
Given `n` and a blacklist of distinct values in `[0, n)`, `pick()` returns a
uniformly random value in `[0, n)` that is **not** blacklisted. Minimise the
number of RNG calls per pick.

That last sentence is the problem. `n` reaches 10⁹ while the blacklist is at
most 10⁵, so anything O(n) — an allow-list array, a shuffled pool — is out on
memory before you start.

The tempting answer is: draw uniformly in `[0, n)` and retry on a blacklisted
hit. It is correct, and its expected cost is `n / (n − b)` draws. Say the
number: with n = 10⁵ and b = 10⁵ − 1 that is 100,000 RNG calls per pick, and
no bound on the worst case. Rejection sampling is fine when rejections are
rare; here the interviewer has arranged for them not to be.
""",
        ),
        (
            "The insight",
            """
Let `m = n − b` be the number of survivors. Then **one** draw in `[0, m)` is
enough, if you first arrange for every index in `[0, m)` to stand for a
distinct valid value.

Some of `[0, m)` is blacklisted, and that is the only problem. Fix it by
pairing off:

- values in `[0, m)` that are blacklisted — the holes;
- values in `[m, n)` that are **not** blacklisted — the spares.

There are exactly as many of each. Every blacklisted entry is either in
`[0, m)` (a hole) or in `[m, n)` (where it displaces a spare), so
`holes = b − (blacklisted in [m, n)) = spares`. Build a hash map hole → spare
once, in O(b), then:

```python
i = random.randrange(self.m)
return self.remap.get(i, i)
```

One RNG call, one hash lookup, worst case bounded. The map holds at most b
entries, never n. This is the same "compress the live values into a dense
prefix" move as
[Insert Delete GetRandom O(1)](../insert-delete-getrandom-o1/) — different
question, identical shape.
""",
        ),
        (
            "Building the remap, and where it goes wrong",
            """
```python
blocked = set(blacklist)
spare = (v for v in range(self.m, n) if v not in blocked)
self.remap = {b: next(spare) for b in blacklist if b < self.m}
```

A generator over the tail, consumed once. The counting argument above is what
guarantees `next(spare)` never raises — worth stating rather than hoping,
because a `StopIteration` inside a dict comprehension is an ugly way to
discover you got the arithmetic wrong.

The failure modes:

- **Scanning the tail per hole** instead of walking it once turns the build
  into O(b·(n − m)). Advance the generator; do not restart it.
- **Drawing in `[0, n)` and then remapping.** The draw must be over `[0, m)`,
  or blacklisted tail values stay reachable.
- **Not skipping blacklisted spares.** `range(m, n)` contains blacklisted
  values too; hand one out and you have swapped one bug for another.
- **Blacklist entries at or above `m` need no entry.** They are never drawn,
  so putting them in the map is harmless but wasteful — and testing `b < m`
  is what keeps the map at O(holes).

Edge cases to name: an empty blacklist (the map is empty and `pick` is a plain
`randrange(n)`), a blacklist covering all but one value (that value is
returned every time), and `m = 0`, which the constraints forbid but which would
make `randrange(0)` raise — guard it if this were production code.
""",
        ),
    ],
}


class Solution:
    def __init__(self, n: int, blacklist: list[int]) -> None:
        self.m = n - len(blacklist)  # survivors, all packed into [0, m)
        blocked = set(blacklist)
        spare = (value for value in range(self.m, n) if value not in blocked)
        # Exactly as many holes below m as there are spares above it.
        self.remap = {value: next(spare) for value in blacklist if value < self.m}

    def pick(self) -> int:
        i = random.randrange(self.m)  # one draw, no retries
        return self.remap.get(i, i)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # No blacklist: a plain uniform draw, empty map.
    plain = Solution(1, [])
    assert plain.remap == {}
    assert all(plain.pick() == 0 for _ in range(100))

    # Everything blacklisted but one value.
    forced = Solution(4, [0, 1, 2])
    assert all(forced.pick() == 3 for _ in range(200))

    # Blacklist entirely in the tail: nothing to remap.
    tail_only = Solution(5, [3, 4])
    assert tail_only.remap == {}
    assert {tail_only.pick() for _ in range(300)} == {0, 1, 2}

    # Blacklist entirely in the head: every draw is remapped.
    head_only = Solution(5, [0, 1])
    assert head_only.remap == {0: 3, 1: 4}
    assert {head_only.pick() for _ in range(300)} == {2, 3, 4}

    # The mixed case, given out of order, with a blacklisted value sitting in
    # the tail so the spare generator has to skip it.
    mixed = Solution(7, [5, 2, 3])  # m = 4; hole 2 and 3 -> spares 4 and 6
    assert sorted(mixed.remap) == [2, 3]
    assert sorted(mixed.remap.values()) == [4, 6]

    draws = 40_000
    spread = Counter(mixed.pick() for _ in range(draws))
    assert set(spread) == {0, 1, 4, 6}, "blacklisted values must be unreachable"
    for value, count in spread.items():
        assert abs(count - draws / 4) < 500, f"{value} came up {count} times"

    # A large n with a small blacklist: memory follows the blacklist, not n.
    sparse = Solution(1_000_000, [0, 999_999, 12_345])
    assert sparse.m == 999_997
    assert len(sparse.remap) == 2  # 999_999 is above m and needs no entry
    for _ in range(2_000):
        value = sparse.pick()
        assert 0 <= value < 1_000_000
        assert value not in {0, 999_999, 12_345}

    # Every survivor must be reachable when n is small enough to enumerate.
    dense = Solution(10, [1, 4, 7, 8])
    assert {dense.pick() for _ in range(2_000)} == {0, 2, 3, 5, 6, 9}
