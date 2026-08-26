"""Implement Rand10() Using Rand7() — LeetCode 470."""

from __future__ import annotations

import random
from collections import Counter

META = {
    "pattern": "randomized",
    "insight": "Two rolls index a 7x7 grid of 49 equally likely cells; keep the first 40 and re-roll the rest, because only rejection preserves uniformity.",
    "time": "O(1) expected — 2.45 calls to rand7 on average, unbounded worst case",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
You are given `rand7()`, uniform on 1…7. Build `rand10()`, uniform on 1…10,
using no other source of randomness.

The constraint that shapes everything: 10 does not divide any power of 7. No
fixed number of `rand7()` calls can ever produce a uniform 1-in-10, because
7^k possibilities cannot be split into 10 equal buckets. So the answer *must*
be a loop, and the interviewer is checking whether you notice that before you
start writing arithmetic.

Worth asking what they want optimised: expected number of `rand7()` calls
(the usual answer) or worst-case latency (there is none — the loop is
unbounded, though the probability of 10 rounds is 0.2^10).
""",
        ),
        (
            "The insight",
            """
Two rolls give a uniform point in a **7×7 grid**:

```
index = (rand7() - 1) * 7 + rand7()     # uniform on 1…49
```

Each of the 49 cells has probability 1/49 — that is the crucial step, and it
only works because the two rolls are independent and the arithmetic is a
bijection onto 1…49.

49 is not a multiple of 10, so **throw away the remainder**. Keep 1…40, reject
41…49 and roll again. Conditioned on acceptance, each of the 40 survivors
still has equal probability, and 40 splits evenly into ten groups of four:

```
(index - 1) % 10 + 1
```

That conditioning argument — "rejection does not disturb the relative
probabilities of what remains" — is the entire proof, and it is the reusable
idea. Rejection sampling is how you convert *any* uniform source into any
other uniform range.
""",
        ),
        (
            "The bias trap, and the cost of rejection",
            """
Every shortcut that avoids the loop is biased, and they are all popular:

- `rand7() + rand7()` — a triangular distribution. 8 is six times as likely as
  2. It is dice, not a uniform draw.
- `(rand7() * rand7()) % 10 + 1` — products collide; 1..10 is not even hit
  uniformly, and some residues are unreachable.
- Rolling 1…49 and using `index % 10 + 1` **without** rejecting — indices 41…49
  give the values 1…9 an extra hit each, so those come up 5/49 while 10 comes
  up 4/49. A **25% skew** on nine of the ten outcomes, and nothing about the
  output looks wrong.

That last one is the one people actually write, and it is invisible without a
histogram. The `check()` below draws 200,000 samples and asserts every value
lands within 0.4% of 20,000; the no-rejection version misses by 1,800.

**The cost.** Acceptance probability is 40/49 ≈ 0.816, so the expected number
of rounds is 49/40 = 1.225 and the expected `rand7()` calls are **2.45**. If
asked to do better: the standard refinement recycles the 9 rejected values
(9 × 7 = 63 → keep 60) and gets to about 2.2 calls. Mention it, and mention
that the loop is unbounded in the worst case but terminates with probability 1.
""",
        ),
    ],
}


def rand7() -> int:
    """The given primitive: uniform on 1…7."""
    return random.randint(1, 7)


def _map_index(index: int) -> int:
    """Fold an accepted 1…40 draw onto 1…10, four indices per value."""
    return (index - 1) % 10 + 1


def rand10() -> int:
    while True:
        index = (rand7() - 1) * 7 + rand7()  # uniform on 1…49
        if index <= 40:  # reject 41…49; the survivors stay uniform
            return _map_index(index)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # The fold is exactly uniform by construction — assert it deterministically
    # rather than statistically. Each value must own precisely four indices.
    folded = Counter(_map_index(index) for index in range(1, 41))
    assert set(folded) == set(range(1, 11))
    assert set(folded.values()) == {4}

    # The primitive itself stays in range.
    assert all(1 <= rand7() <= 7 for _ in range(1_000))

    # End-to-end histogram. Skipping rejection gives 1…9 five indices each and
    # 10 only four, which lands 1,800 off here.
    draws = 200_000
    spread = Counter(rand10() for _ in range(draws))
    assert set(spread) == set(range(1, 11))
    for value, count in spread.items():
        assert abs(count - draws / 10) < 800, f"rand10 produced {value} {count} times"

    # Expected rand7 calls per rand10: 2 * 49/40 = 2.45. A version that loops
    # on a wider rejection window, or re-rolls both dice needlessly, exceeds 3.
    global rand7
    original = rand7
    tally = [0]

    def counting_rand7() -> int:
        tally[0] += 1
        return original()

    rand7 = counting_rand7
    try:
        for _ in range(20_000):
            rand10()
    finally:
        rand7 = original
    assert 2.0 < tally[0] / 20_000 < 3.0, f"{tally[0] / 20_000:.3f} rand7 calls per rand10"
