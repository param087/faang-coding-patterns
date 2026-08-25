"""Subarray Sum Equals K — LeetCode 560."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "prefix-sums",
    "insight": "A subarray ending here sums to k exactly when running - k is a prefix you have already seen.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count the contiguous subarrays summing to exactly `k`.

**Ask about negatives first.** It is the question that decides your whole
approach, and the answer is yes.
""",
        ),
        (
            "Why not a sliding window",
            """
A window relies on the sum being monotone as the window grows, so that
shrinking from the left is a meaningful correction. With negative numbers,
extending the window can *decrease* the sum, and the argument collapses.

Say this out loud:

> "A sliding window would be O(1) space, but the constraints allow negatives,
> so the sum isn't monotone and the window doesn't apply."

Reaching for a window here is the most common wrong first answer in
interviews, and noticing why it fails is a strong signal.
""",
        ),
        (
            "The insight",
            """
Let `running` be the prefix sum up to the current index. A subarray ending
here sums to `k` exactly when some earlier prefix equalled `running - k`.

So instead of trying every start point, look up **how many** valid start
points there were. That is a hash map of prefix sums seen so far.

This is the same reframing as Two Sum — stop searching for the partner, ask
whether the partner has already gone past — applied to running totals instead
of values.
""",
        ),
        (
            "The seed",
            """
`seen[0] = 1` represents the **empty prefix**, and it is what makes subarrays
starting at index 0 count.

It is a count of one, not zero. Getting this wrong loses every answer that
begins at the start of the array, and it passes several test cases first.
""",
        ),
        (
            "Dry run",
            """
`[1, -1, 0], k = 0`

Running totals are 1, 0, 0. Seeded with `{0: 1}`.

- i=0: `running = 1`, want `1 - 0 = 1` — unseen. Count 0. Record `{0:1, 1:1}`.
- i=1: `running = 0`, want 0 — seen once. **Count 1.** Record `{0:2, 1:1}`.
- i=2: `running = 0`, want 0 — seen twice. **Count 3.**

Three subarrays: `[1,-1]`, `[0]`, `[1,-1,0]`. The negative and the zero are
both there deliberately — run this, not `[1,1,1]`.
""",
        ),
        (
            "Follow-ups",
            """
- **Longest subarray summing to k** — same scan, but store the *first* index
  each prefix was seen at and track a maximum length. Storing the latest index
  gives the shortest, which is the classic slip.
- **Subarray Sums Divisible by K** — key on `running % k` instead.
- **Contiguous Array** (equal 0s and 1s) — relabel 0 as −1 and this becomes
  "sums to zero".
""",
        ),
    ],
}


def subarray_sum(nums: list[int], k: int) -> int:
    seen: dict[int, int] = defaultdict(int)
    seen[0] = 1  # the empty prefix, counted once
    running = 0
    count = 0

    for value in nums:
        running += value
        count += seen[running - k]
        seen[running] += 1

    return count


CASES = [
    (([1, 1, 1], 2), 2),
    (([1, 2, 3], 3), 2),
    (([1, -1, 0], 0), 3),
    (([3, 4, 7, 2, -3, 1, 4, 2], 7), 4),
    (([1], 0), 0),
    (([], 0), 0),
]


def solve(nums: list[int], k: int) -> int:
    return subarray_sum(nums, k)
