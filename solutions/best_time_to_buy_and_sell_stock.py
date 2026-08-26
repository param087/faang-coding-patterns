"""Best Time to Buy and Sell Stock — LeetCode 121."""

from __future__ import annotations

META = {
    "pattern": "sliding-window",
    "insight": "Carry the cheapest price seen so far; every day already knows its best possible sale in one subtraction.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
One buy and one sell, the buy strictly before the sell. Return the largest
profit, or `0` if every ordering loses money.

Ask two things. **Can I short?** (No — sell must come after buy, which is the
whole constraint.) **Is the answer the profit or the two days?** If it is the
days, you also need to remember where the minimum was, and the code changes.

This is a window whose left edge only ever jumps to a new cheapest day: the
degenerate, most useful case of the pattern.
""",
        ),
        (
            "The insight",
            """
The naive answer is every pair `(i, j)` with `i < j` — 5·10⁹ pairs at
n = 10⁵, so it is not an answer.

Flip the question from "which pair?" to "for **this** selling day, what is the
best I could have bought at?". That is `min(prices[:i])`, and it is a running
minimum: one variable, updated as you scan.

So each day does two O(1) things — score itself against the running minimum,
then possibly become the new minimum. One pass, no lookahead.

Note the order inside the loop. Score first, then update the minimum. Do it
the other way and a single day can buy and sell from itself, giving profit 0
where the real answer might matter — harmless here, but the same slip is fatal
in the "with cooldown" and "with fee" variants.
""",
        ),
        (
            "Edge cases",
            """
- **Monotonically decreasing prices** — the answer is `0`, not a negative
  number. Initialising `best = 0` rather than `-inf` encodes "do not trade".
- **Empty or single-element input.** `prices[0]` on an empty list is the
  crash an interviewer will look for; guard it.
- **Flat prices** `[3, 3, 3]` → `0`, and this is the case that catches a
  strict-versus-non-strict comparison bug.
- **The one-liner "max minus min"** is wrong whenever the maximum comes first:
  `[7, 1]` would give 6. Order is the entire problem.
""",
        ),
    ],
}


def max_profit(prices: list[int]) -> int:
    if not prices:
        return 0

    cheapest = prices[0]
    best = 0

    for price in prices[1:]:
        best = max(best, price - cheapest)  # sell today, having bought at the minimum
        cheapest = min(cheapest, price)  # only then can today become the buy day

    return best


CASES = [
    (([7, 1, 5, 3, 6, 4],), 5),
    (([7, 6, 4, 3, 1],), 0),
    (([2, 4, 1],), 2),
    (([2, 1, 2, 1, 0, 1, 2],), 2),
    (([3, 3, 3],), 0),
    (([1, 2],), 1),
    (([5],), 0),
    (([],), 0),
]


def solve(prices: list[int]) -> int:
    return max_profit(prices)
