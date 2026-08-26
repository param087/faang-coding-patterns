"""Best Time to Buy and Sell Stock IV — LeetCode 188."""

from __future__ import annotations

META = {
    "pattern": "dp-advanced",
    "insight": "The four states of the two-transaction version become 2k states, and once k passes n/2 the cap stops binding at all.",
    "time": "O(nk), or O(n) once k >= n/2",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
At most `k` transactions, one position at a time, maximise profit. LeetCode
123 is this with `k = 2` and 121 is this with `k = 1`.

Clarify that `k` is a **cap**, not a quota, and that `k` can be far larger
than the array — the constraints allow `k` up to 100 with `n` up to 1000,
which is exactly the regime where the naive O(nk) table does 100× more work
than the problem contains.
""",
        ),
        (
            "The insight",
            """
Two things carry the answer.

**1. Generalise the state machine.** Keep `buy[t]` = best cash while holding
the `t`-th position and `sell[t]` = best cash after closing it:

```
buy[t]  = max(buy[t],  sell[t-1] - price)
sell[t] = max(sell[t], buy[t]   + price)
```

`sell[0] = 0` anchors the recurrence. Sweeping `t` upward inside the price
loop is safe for the same reason as in 123: reading the `buy[t]` written this
iteration models buying and selling on the same day, worth zero.

**2. Collapse the cap when it cannot bind.** A transaction needs one day to
buy and a different day to sell, so at most `n // 2` disjoint transactions fit
in `n` days. If `k >= n // 2` the cap is irrelevant and the answer is the
greedy one from LeetCode 122 — **sum every positive day-to-day rise** — in
O(n) with no table.

Skipping that check is the actual failure mode of this problem: with
`k = 10**9` the honest DP allocates two arrays of a billion entries and dies
before it computes anything. Interviewers set `k` large on purpose.
""",
        ),
        (
            "Edge cases",
            """
- **`k = 0`** or fewer than two prices: 0. Handle before allocating.
- **The greedy branch must be the *unbounded* answer**, not `k` copies of
  anything. `sum(max(b - a, 0))` telescopes: buying at every local minimum and
  selling at every local maximum yields exactly that sum.
- **Descending prices**: both branches return 0, because every `sell[t]` stays
  at its 0 seed and every positive rise is absent.
- **Seed `buy[t]` at −infinity**, one per level. Seeding at 0 hands you a free
  position and inflates the answer by the first price.
- **Where the money is capped**: `sell[k]` is monotone in `k`, so returning
  `sell[k]` — not `max(sell)` — is already correct, though `max(sell)` is a
  harmless equivalent that costs an extra pass.
- Follow-up worth naming: adding a **cooldown** (309) or a **fee** (714) is a
  one-line change to the same recurrence — subtract the fee inside `sell`, or
  fund `buy[t]` from `sell[t-1]` two days back.
""",
        ),
    ],
}


def max_profit(k: int, prices: list[int]) -> int:
    n = len(prices)
    if k <= 0 or n < 2:
        return 0

    # A transaction burns two distinct days, so more than n // 2 of them can
    # never fit: the cap stops binding and the greedy answer to LC 122 is exact.
    if k >= n // 2:
        return sum(max(b - a, 0) for a, b in zip(prices, prices[1:], strict=False))

    buy = [float("-inf")] * (k + 1)  # holding the t-th position
    sell = [0.0] * (k + 1)  # t-th position closed; sell[0] anchors at 0

    for price in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - price)
            sell[t] = max(sell[t], buy[t] + price)

    return int(sell[k])  # monotone in t, so the cap level is the best level


CASES = [
    ((2, [2, 4, 1]), 2),
    ((2, [3, 2, 6, 5, 0, 3]), 7),
    ((2, [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]), 13),
    ((3, [1, 2, 3, 4, 5]), 4),
    ((10**9, [1, 3, 2, 8, 4, 9]), 13),
    ((1, [7, 6, 4, 3, 1]), 0),
    ((0, [1, 3]), 0),
    ((2, []), 0),
]


def solve(k: int, prices: list[int]) -> int:
    return max_profit(k, prices)
