"""Best Time to Buy and Sell Stock II — LeetCode 122."""

from __future__ import annotations

META = {
    "pattern": "greedy",
    "insight": "With unlimited transactions any profitable run decomposes into its up-days, so just bank every rise.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Prices by day, unlimited buy/sell pairs, but you may hold at most one share at
a time. Return the maximum profit.

The clarifying question that matters: **can I buy and sell on the same day?**
Yes — and that is what licenses the one-liner, because it means holding through
a rise and re-buying instantly are the same thing.
""",
        ),
        (
            "The insight",
            """
Buying at a local minimum and selling at the next local maximum earns exactly
the same as selling and re-buying every single day inside that run:

```
p[d] - p[a] = (p[a+1] - p[a]) + (p[a+2] - p[a+1]) + ... + (p[d] - p[d-1])
```

The sum telescopes. So the optimum is the sum of every positive consecutive
difference — no peak/valley bookkeeping, no state machine.

Skipping a positive step can never help (it only removes a positive term), and
including a negative step can never help. That two-line exchange argument is
the proof an interviewer wants; the code is incidental.
""",
        ),
        (
            "Where people over-engineer",
            """
The usual first answer is a peak-and-valley walk with `buying`/`selling` flags,
or the two-state DP `hold = max(hold, free - p)`, `free = max(free, hold + p)`.
Both are correct and both are O(n) — but if you write either without noticing
the telescoping, you have missed the point of the question.

The DP is the right tool the moment a constraint appears: **at most k
transactions** (LeetCode 188), or a **transaction fee** (714), or a **cooldown**
day (309). Under any of those the greedy is flat wrong, because breaking a run
into many small trades now costs money. Say which family you are in before you
write a line.
""",
        ),
    ],
}


def max_profit(prices: list[int]) -> int:
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:], strict=False))


CASES = [
    (([7, 1, 5, 3, 6, 4],), 7),
    (([1, 2, 3, 4, 5],), 4),  # one long run, telescopes to 5 - 1
    (([7, 6, 4, 3, 1],), 0),  # monotone down, never trade
    (([3, 3, 3],), 0),  # flat days contribute nothing
    (([2, 1, 2, 0, 1],), 2),  # two separate runs
    (([5],), 0),
    (([],), 0),
]


def solve(prices: list[int]) -> int:
    return max_profit(prices)
