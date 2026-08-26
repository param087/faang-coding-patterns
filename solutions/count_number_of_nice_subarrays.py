"""Count Number of Nice Subarrays — LeetCode 1248."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "prefix-sums",
    "insight": "Replace each number by its parity bit and the question becomes: how many subarrays sum to exactly k.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count the contiguous subarrays containing exactly `k` odd numbers. The even
numbers are noise — only parity matters, and the actual values never do.

Say that first, because the rewrite is the answer: map `x -> x & 1` and you are
counting subarrays that sum to `k` over a 0/1 array.
""",
        ),
        (
            "The insight",
            """
Brute force is `O(n²)` subarrays; at `n = 5·10⁴` that is 2.5·10⁹ — dead.

With `prefix[i]` = number of odds in `nums[0..i)`, a subarray `(l, r]` is nice
exactly when `prefix[r] - prefix[l] == k`. So walk left to right keeping the
running count of odds, and at each position add **how many earlier prefixes
equalled `running - k`**. One pass, one hash map.

Seed the map with `{0: 1}`, standing for the empty prefix before index 0.
That single entry is what makes a subarray starting at index 0 countable;
without it `[1]` with `k = 1` returns 0.

Two details worth stating:

- The map is keyed by a **count of matches, not a boolean**. `[2,2,2]` with
  `k = 0` has prefix 0 four times and the answer is C(4,2) = 6 — the pairs are
  what you are counting.
- Because every value is 0 or 1 the prefix is non-decreasing, so a plain
  `list` of size `n+1` indexed by count works just as well as a dict and is
  faster. Mention it; write the dict, because the dict version survives the
  follow-up where the values are arbitrary.
""",
        ),
        (
            "Follow-ups",
            """
- **"Do it in O(1) extra space."** Store only the positions of the odd numbers
  (or, better, the gap of evens before each odd). For the window whose odd
  count is `k`, the number of subarrays is `(evens before the first odd + 1) ×
  (evens after the last odd + 1)`. Two pointers, no map.
- **"Exactly k" as a general shape.** `exactly(k) = atMost(k) - atMost(k-1)`,
  where `atMost` is a sliding window. That decomposition is the reusable trick
  — it also solves Subarrays with K Different Integers and Binary Subarrays
  With Sum, where a prefix map is clumsier.
- **Values instead of parity** — Subarray Sum Equals K, LeetCode 560. Same
  code with `running += x` instead of `running += x & 1`. The parity mapping is
  the only thing this problem adds, which is why it is worth spotting quickly.
""",
        ),
    ],
}


def number_of_subarrays(nums: list[int], k: int) -> int:
    seen: defaultdict[int, int] = defaultdict(int)
    seen[0] = 1  # the empty prefix, so subarrays starting at index 0 count

    odds = 0
    total = 0
    for value in nums:
        odds += value & 1
        total += seen[odds - k]  # every earlier prefix that leaves exactly k
        seen[odds] += 1

    return total


CASES = [
    (([1, 1, 2, 1, 1], 3), 2),
    (([2, 4, 6], 1), 0),
    (([2, 2, 2, 1, 2, 2, 1, 2, 2, 2], 2), 16),
    (([1, 1, 1], 1), 3),
    (([1], 1), 1),
    (([1], 2), 0),
    (([2, 2, 2], 0), 6),
    (([], 1), 0),
]


def solve(nums: list[int], k: int) -> int:
    return number_of_subarrays(nums, k)
