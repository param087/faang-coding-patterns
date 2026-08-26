"""Longest Increasing Subsequence — LeetCode 300."""

from __future__ import annotations

from bisect import bisect_left

META = {
    "pattern": "dp-1d",
    "insight": "tails[k] is the smallest possible tail of an increasing subsequence of length k+1 — sorted, so binary search places each value.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
The length of the longest **strictly increasing subsequence**. Not contiguous.

Ask: strictly increasing or non-decreasing (**strict** on LeetCode — and it is
`bisect_left` versus `bisect_right`, a one-word change); subsequence rather
than substring (yes); return the length or the sequence.
""",
        ),
        (
            "The O(n²) DP first",
            """
`dp[i]` = the length of the LIS **ending at** `i`. For each `i`, scan all
earlier `j` with `nums[j] < nums[i]` and take the best.

State it, give the complexity, confirm it is correct. It is the honest
starting point and it is what generalises to variants like Russian Doll
Envelopes.
""",
        ),
        (
            "The O(n log n) version",
            """
Keep `tails`, where `tails[k]` is the **smallest possible tail** of an
increasing subsequence of length `k + 1`.

`tails` is necessarily sorted, so binary search finds where each new value
belongs. If it extends beyond the end, the LIS got longer; otherwise it
*replaces* the first tail that is not smaller — because a smaller tail is
strictly better for everything that follows.
""",
        ),
        (
            "The honest caveat",
            """
**`tails` is not a valid subsequence.** Only its *length* is meaningful.

The values in it may never have appeared together in that order. Interviewers
ask this precisely to see whether you understand the algorithm or recall it —
do not claim otherwise.

Reconstructing the actual subsequence needs a parent array recorded alongside.
""",
        ),
        (
            "Dry run",
            """
`[10, 9, 2, 5, 3, 7, 101, 18]`

`tails` evolves: `[10] → [9] → [2] → [2,5] → [2,3] → [2,3,7] → [2,3,7,101] →
[2,3,7,18]`. Length **4**.

Note the `5 → 3` replacement: the length did not change, but the tail got
smaller, which is what makes room for 7 later.
""",
        ),
        (
            "Follow-ups",
            """
- **Russian Doll Envelopes** — sort by width ascending and height
  **descending**, then LIS on heights. The descending tie-break stops two
  envelopes of equal width both counting, and spotting it is the entire
  difficulty of that problem.
- **Number of Longest Increasing Subsequences** — the O(n log n) trick does not
  extend; you need the O(n²) DP with a count array, or a segment tree.
- **Non-decreasing** — `bisect_right` instead of `bisect_left`.
""",
        ),
    ],
}


def length_of_lis(nums: list[int]) -> int:
    tails: list[int] = []  # tails[k] = smallest tail of an LIS of length k+1

    for value in nums:
        # bisect_left for STRICTLY increasing; bisect_right allows equals.
        position = bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)  # extends the longest subsequence
        else:
            tails[position] = value  # a smaller tail is strictly better

    return len(tails)


def length_of_lis_quadratic(nums: list[int]) -> int:
    """The O(n^2) DP — the honest starting point, and what variants extend."""
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


CASES = [
    (([10, 9, 2, 5, 3, 7, 101, 18],), 4),
    (([0, 1, 0, 3, 2, 3],), 4),
    (([7, 7, 7, 7],), 1),
    (([1, 2, 3, 4, 5],), 5),
    (([5, 4, 3, 2, 1],), 1),
    (([4],), 1),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return length_of_lis(nums)


def check() -> None:
    for args, expected in CASES:
        assert length_of_lis(*args) == expected
        # The two formulations must agree.
        assert length_of_lis_quadratic(*args) == expected
