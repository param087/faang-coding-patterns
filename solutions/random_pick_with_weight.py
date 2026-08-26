"""Random Pick with Weight — LeetCode 528."""

from __future__ import annotations

import random
from bisect import bisect_left
from collections import Counter

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Prefix sums lay the weights out as contiguous segments on a line; a uniform draw lands in one with exactly the right probability.",
    "time": "O(n) build, O(log n) per pick",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given weights `w`, return index `i` with probability `w[i] / sum(w)`.

Ask: are weights positive integers (yes); how many picks relative to the
number of weights (many — which is what justifies the O(n) preprocessing); can
the weights change after construction (no, and if they could the answer
differs).
""",
        ),
        (
            "The insight",
            """
Lay the weights out end to end on a number line. Weight 1 owns `[0, 1)`,
weight 3 owns `[1, 4)`, and so on — the boundaries are exactly the **prefix
sums**.

A uniform draw into `[0, total)` lands in a segment with probability
proportional to that segment's length, which is precisely the required
distribution. Binary search finds which segment.

O(n) to build the prefix array once, then O(log n) per pick.
""",
        ),
        (
            "The bound is the bug",
            """
`bisect_left` against the prefix totals, with the draw shifted into
`[1, total]`.

Using `bisect_right` shifts every pick by one and quietly gives index `i`'s
weight to index `i+1`. The output still looks random, and it is wrong — which
is the worst kind of bug, because no small test case reveals it.

**Verify with a histogram**, not with an eyeball. The test below draws 60,000
samples and asserts the empirical ratio matches the weights.
""",
        ),
        (
            "Dry run",
            """
`w = [1, 3]`, prefix `[1, 4]`.

- A draw in `[1, 1]` → `bisect_left([1,4], 1)` = 0. Probability 1/4. ✓
- A draw in `[2, 4]` → index 1. Probability 3/4. ✓

Check the boundary at exactly 1 — that is what distinguishes the two bisect
variants.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if the weights change?"** The prefix array is O(n) to rebuild, so
  you want a [Fenwick tree](../../patterns/segment-tree/) over the weights,
  with the pick becoming a descent through it in O(log n).
- **Random Pick with Blacklist** — remap blacklisted indices into the tail, so
  a single uniform draw over the reduced range works.
- **Random Point in Non-overlapping Rectangles** — this exact technique,
  weighted by rectangle area.
""",
        ),
    ],
}


class Solution:
    def __init__(self, w: list[int]) -> None:
        self.prefix: list[int] = []
        running = 0
        for weight in w:
            running += weight
            self.prefix.append(running)  # segment boundaries on the number line
        self.total = running

    def pick_index(self) -> int:
        # Draw in [1, total], then bisect_left finds the owning segment.
        target = random.randint(1, self.total)
        return bisect_left(self.prefix, target)


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    single = Solution([1])
    assert all(single.pick_index() == 0 for _ in range(50))

    # A distribution bug cannot be caught by eye — check the histogram.
    weights = [1, 3]
    picker = Solution(weights)
    draws = 60_000
    counts = Counter(picker.pick_index() for _ in range(draws))
    assert set(counts) == {0, 1}
    expected_zero = draws * weights[0] / sum(weights)
    # Generous tolerance: this is a statistical test, not an exact one.
    assert abs(counts[0] - expected_zero) < draws * 0.03

    # Zero-weight entries must never be selected.
    sparse = Solution([0, 5, 0])
    assert all(sparse.pick_index() == 1 for _ in range(200))

    uniform = Solution([2, 2, 2])
    spread = Counter(uniform.pick_index() for _ in range(30_000))
    assert set(spread) == {0, 1, 2}
    for index in (0, 1, 2):
        assert abs(spread[index] - 10_000) < 900
