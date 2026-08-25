"""House Robber — LeetCode 198."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "At each house: skip it and keep the best so far, or take it and add the best from two houses back.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Maximum sum of a subset of the array with **no two adjacent** elements.

Ask: are values non-negative (yes — with negatives, "skip everything" becomes
an option and the base cases change); is the row circular (that is House
Robber II); can the array be empty.
""",
        ),
        (
            "State first",
            """
Say this sentence before writing anything:

> `dp[i]` = the most I can steal from the first `i` houses.

Most failed DP is a state failure rather than a coding one. Naming the state
out loud tells the interviewer you have solved it before you touch the
keyboard.
""",
        ),
        (
            "The recurrence",
            """
`dp[i] = max(dp[i-1], dp[i-2] + nums[i])` — either skip this house and keep
what was best one back, or take it and add what was best two back.

This take-or-skip shape is the most common 1-D DP there is; recognising it
transfers to Delete and Earn, Best Time to Buy and Sell Stock with Cooldown,
and a dozen others.
""",
        ),
        (
            "Fold the table",
            """
Only `dp[i-1]` and `dp[i-2]` are ever read, so the array collapses to two
variables and the space becomes O(1).

**Do the fold in the round.** Write the array first if it helps you think,
then say "only the last two entries are read, so I can drop the array" and do
it. It is a free demonstration of understanding.
""",
        ),
        (
            "Dry run",
            """
`[2, 1, 1, 2]` → **4** (first and last houses).

Worth running because the obvious greedy — "always take the larger neighbour"
— gets 3 here. That counterexample is the reason this is DP and not greedy,
and it is worth pointing at.
""",
        ),
        (
            "Follow-ups",
            """
- **House Robber II**, houses in a circle. The first and last are now
  adjacent, so run the linear version **twice** — once excluding the first
  house, once excluding the last — and take the max. That reduction is the
  entire solution.
- **House Robber III**, a binary tree. Each node returns a *pair*: best if
  robbed, best if not. See [Advanced DP](../../patterns/dp-advanced/).
""",
        ),
    ],
}


def rob(nums: list[int]) -> int:
    take, skip = 0, 0  # best ending here having taken / skipped this house

    for value in nums:
        take, skip = skip + value, max(skip, take)

    return max(take, skip)


CASES = [
    (([1, 2, 3, 1],), 4),
    (([2, 7, 9, 3, 1],), 12),
    (([2, 1, 1, 2],), 4),
    (([5],), 5),
    (([2, 1],), 2),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return rob(nums)
