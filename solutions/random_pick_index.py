"""Random Pick Index — LeetCode 398."""

from __future__ import annotations

import random
from collections import Counter

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Keep the k-th matching index with probability 1/k as you scan — a one-slot reservoir needs no storage at all.",
    "time": "O(n) per pick, O(1) build",
    "space": "O(1) beyond the input",
    "sections": [
        (
            "What it asks",
            """
Given an array with duplicates, `pick(target)` returns a **uniformly random**
index `i` with `nums[i] == target`. The target is guaranteed to exist.

The clarifying question decides the whole answer: **how much extra memory may
I use?** LeetCode's follow-up forbids the obvious `value → list of indices`
map, which is what makes this a reservoir-sampling problem rather than a
one-line hash map.

Also ask how many picks per array. Many picks on a fixed array favours the
map; a handful of picks, or an array you are streaming past once, favours the
reservoir.
""",
        ),
        (
            "The insight",
            """
Reservoir sampling with a reservoir of size 1.

Scan once, counting matches. When you meet the k-th match, keep it with
probability **1/k** and otherwise leave the currently held index alone. At the
end, whatever you are holding is uniform over all matches.

The proof is a telescoping product. Match k is held at the end if it was taken
(1/k) and never displaced by any later match (∏ from j = k+1 to m of
(1 − 1/j) = k/m). Multiply: (1/k)·(k/m) = **1/m**, independent of k.

The property that matters beyond this problem: it is uniform at *every*
prefix, not only at the end. That is why the same code works on a stream whose
length you do not know in advance.
""",
        ),
        (
            "Which structure they actually want",
            """
Two answers, and you should price both out loud:

```
                          build   pick   space
value -> list of indices   O(n)   O(1)    O(n)
one-slot reservoir         O(1)   O(n)    O(1)
```

With q picks the map costs O(n + q) and the reservoir O(nq). For a
10⁴-element array and 10⁴ picks that is 10⁸ operations versus 2·10⁴ — so if
memory is free, the map wins and saying otherwise is showing off. The
reservoir earns its place only when the array does not fit, or when it arrives
as a stream.

Two implementation notes that catch people:

- `random.randrange(seen) == 0` with `seen` the 1-based match count. Writing
  `randrange(seen - 1)` or comparing against `seen` is the off-by-one that
  quietly starves the first match.
- Copy the input in the constructor. If the caller mutates their list
  afterwards, a shared reference turns `pick` into a heisenbug.
""",
        ),
    ],
}


class Solution:
    def __init__(self, nums: list[int]) -> None:
        self.nums = list(nums)  # copy: the caller may mutate theirs

    def pick(self, target: int) -> int:
        chosen = -1
        seen = 0
        for i, value in enumerate(self.nums):
            if value != target:
                continue
            seen += 1
            if random.randrange(seen) == 0:  # keep the k-th match w.p. 1/k
                chosen = i
        return chosen


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    picker = Solution([1, 2, 3, 3, 3])

    # A target with a single occurrence is deterministic.
    assert all(picker.pick(1) == 0 for _ in range(100))
    assert all(picker.pick(2) == 1 for _ in range(100))

    # A missing target returns the sentinel rather than looping forever.
    assert picker.pick(99) == -1

    # Uniformity over the three 3s. A reservoir that keeps the last match
    # always returns 4; one that keeps the first always returns 2.
    draws = 30_000
    spread = Counter(picker.pick(3) for _ in range(draws))
    assert set(spread) == {2, 3, 4}
    for index in (2, 3, 4):
        assert abs(spread[index] - draws / 3) < 500, f"index {index}: {spread[index]}"

    # Matches at both ends of the array, and negatives.
    edges = Solution([-5, 0, 7, 0, -5])
    ends = Counter(edges.pick(-5) for _ in range(20_000))
    assert set(ends) == {0, 4}
    assert abs(ends[0] - 10_000) < 500

    # Every element identical: uniform over all n indices.
    flat = Solution([4] * 6)
    all_same = Counter(flat.pick(4) for _ in range(30_000))
    assert set(all_same) == set(range(6))
    assert all(abs(count - 5_000) < 400 for count in all_same.values())

    # The constructor's copy must insulate against later mutation.
    caller_list = [8, 9]
    guarded = Solution(caller_list)
    caller_list.append(8)
    assert all(guarded.pick(8) == 0 for _ in range(50))
