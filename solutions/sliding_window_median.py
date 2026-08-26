"""Sliding Window Median — LeetCode 480."""

from __future__ import annotations

import heapq
import random
from collections import Counter

META = {
    "pattern": "heaps",
    "symbol": "median_sliding_window",
    "insight": "Two heaps give the median, but a window also removes — mark departures dead, evict only at the root, and count live sizes yourself.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Slide a window of width k across the array and report the median of each
window, as a float.

Ask two things before writing anything:

- **How large is k relative to n?** With n = 10⁵ and k = 10⁴, an O(n·k)
  solution is 10⁹ operations and times out; with k ≤ 20 the naive re-sort is
  genuinely fine and much shorter.
- **Even-width medians** are the average of the two middle values, so the
  return type is `float` even for integer input. Say it, because the odd case
  returning an int is a common silent mismatch.

Also worth flagging: LeetCode uses `2³¹ − 1` values here specifically to break
`(lo + hi) / 2` in fixed-width languages. Python has bignums, so mention the
overflow and move on.
""",
        ),
        (
            "The insight",
            """
Median from a stream is the classic two-heap problem: a max-heap of the lower
half, a min-heap of the upper half, median read off the roots in O(1). A
window is that problem plus **removals**, and a binary heap cannot delete an
arbitrary interior element — only its root.

So do not delete. **Lazy deletion**: when a value leaves the window, record it
in a `delayed` counter and leave the physical entry in place. Whenever a heap's
root turns out to be a marked value, pop it then. Every element is pushed once
and popped at most once, so the amortised cost stays O(log n) per step even
though a single step can pop several stale roots.

The part that actually decides correctness is **size accounting**. The heaps
now contain ghosts, so `len(small)` is meaningless — you must track
`small_size` and `large_size` as counts of *live* elements and rebalance on
those. Every wrong implementation of this problem gets that wrong.

Invariant to state out loud and then never break: `small_size` is either equal
to `large_size` or exactly one more. Odd k reads the median from `small`'s
root; even k averages both roots.
""",
        ),
        (
            "The traps, in the order people hit them",
            """
- **Rebalancing on `len(heap)`.** Ghosts inflate it. Rebalance on the live
  counters only.
- **Pruning at the wrong time.** After moving a live element across, the newly
  exposed root may be a ghost — prune *after* the transfer, or the next median
  read returns a value that left the window three steps ago.
- **Deciding which side a departing value belongs to.** Compare against
  `-small[0]`, the current boundary: `num <= -small[0]` means it was in the
  lower half. Getting this backwards corrupts the counters silently and the
  output is wrong only in the middle of long runs — brutal to debug.
- **Only prune when the departing value *is* the root.** If it is interior,
  leaving it marked costs nothing and pruning would be O(n).
- **Duplicates.** `delayed` must be a multiset (a `Counter`), not a set:
  `[8, 8, 8]` with k = 2 deletes the value 8 twice and a set would drop both
  copies on the first prune.
- **The alternative worth naming:** an order-statistic tree or a `SortedList`
  gives O(log k) insert, delete *and* k-th element with no ghosts — the two
  heaps exist because most languages ship a heap and not an indexable
  multiset. If a `SortedList` is available, say you would use it.
""",
        ),
    ],
}


class DualHeap:
    """Two heaps with lazy deletion — a multiset that can report its median."""

    def __init__(self, k: int) -> None:
        self.k = k
        self.small: list[int] = []  # lower half, negated (max-heap)
        self.large: list[int] = []  # upper half (min-heap)
        self.delayed: Counter[int] = Counter()  # values removed but still resident
        self.small_size = 0  # live counts — len() would count ghosts
        self.large_size = 0

    def _prune_small(self) -> None:
        while self.small and self.delayed[-self.small[0]]:
            self.delayed[-self.small[0]] -= 1
            heapq.heappop(self.small)

    def _prune_large(self) -> None:
        while self.large and self.delayed[self.large[0]]:
            self.delayed[self.large[0]] -= 1
            heapq.heappop(self.large)

    def _rebalance(self) -> None:
        if self.small_size > self.large_size + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
            self.small_size -= 1
            self.large_size += 1
            self._prune_small()  # the transfer may expose a ghost
        elif self.small_size < self.large_size:
            heapq.heappush(self.small, -heapq.heappop(self.large))
            self.large_size -= 1
            self.small_size += 1
            self._prune_large()

    def insert(self, num: int) -> None:
        if not self.small or num <= -self.small[0]:
            heapq.heappush(self.small, -num)
            self.small_size += 1
        else:
            heapq.heappush(self.large, num)
            self.large_size += 1
        self._rebalance()

    def erase(self, num: int) -> None:
        self.delayed[num] += 1  # marked dead, not removed
        if num <= -self.small[0]:
            self.small_size -= 1
            if num == -self.small[0]:  # only prune when it is the root
                self._prune_small()
        else:
            self.large_size -= 1
            if num == self.large[0]:
                self._prune_large()
        self._rebalance()

    def median(self) -> float:
        if self.k % 2:
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2


def median_sliding_window(nums: list[int], k: int) -> list[float]:
    if k <= 0 or k > len(nums):
        return []

    window = DualHeap(k)
    for num in nums[:k]:
        window.insert(num)

    medians = [window.median()]
    for i in range(k, len(nums)):
        window.insert(nums[i])
        window.erase(nums[i - k])
        medians.append(window.median())
    return medians


def _brute_force(nums: list[int], k: int) -> list[float]:
    """O(n k log k) reference — only used to cross-check the heaps."""
    out = []
    for i in range(len(nums) - k + 1):
        ordered = sorted(nums[i : i + k])
        mid = k // 2
        out.append(float(ordered[mid]) if k % 2 else (ordered[mid - 1] + ordered[mid]) / 2)
    return out


CASES = [
    (([1, 3, -1, -3, 5, 3, 6, 7], 3), [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]),
    (([1, 2, 3, 4, 2, 3, 1, 4, 2], 3), [2.0, 3.0, 3.0, 3.0, 2.0, 3.0, 2.0]),
    (([1, 4, 2, 3], 4), [2.5]),  # even width -> an average, not an element
    (([5], 1), [5.0]),
    (([2147483647, 2147483647], 2), [2147483647.0]),  # the overflow bait
    (([1, 1, 1, 1], 2), [1.0, 1.0, 1.0]),  # duplicates: delayed must be a multiset
    (([7, -7, 7, -7], 2), [0.0, 0.0, 0.0]),
    (([8, 8, 8, 1, 1, 1, 8, 8], 3), [8.0, 8.0, 1.0, 1.0, 1.0, 8.0]),
    (([], 3), []),
]


def check() -> None:
    for index, (args, expected) in enumerate(CASES):
        actual = solve(*args)
        assert actual == expected, f"case {index}: {actual} != {expected}"
        assert actual == _brute_force(*args), f"case {index} disagrees with brute force"

    # Randomised cross-check: heavy duplication is what exposes bad size
    # accounting, so keep the value range small and the windows wide.
    rng = random.Random(11)
    for _ in range(300):
        n = rng.randint(1, 14)
        sample = [rng.randint(-3, 3) for _ in range(n)]
        k = rng.randint(1, n)
        assert median_sliding_window(sample, k) == _brute_force(sample, k), (sample, k)


def solve(nums: list[int], k: int) -> list[float]:
    return median_sliding_window(list(nums), k)
