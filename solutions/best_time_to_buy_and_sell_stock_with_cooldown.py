"""Best Time to Buy and Sell Stock with Cooldown — LeetCode 309."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "Three end-of-day states — holding, just sold, free — and the cooldown is just the missing edge from just-sold to holding.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Unlimited transactions, at most one share held at a time, and after **selling**
you must sit out one day before buying again. Maximise profit.

Ask: does the cooldown apply after buying too? (No — sells only.) Can you buy
and sell on the same day? (Pointless: zero profit and it costs you the cooldown.)
Is there a transaction fee? (Not here — LeetCode 714 is that variant and it
takes the same shape.)

The greedy that solves LeetCode 122 — sum every positive `prices[i] - prices[i-1]`
— is the wrong first answer. On `[1, 2, 3]` it books 1 + 1 = 2 by selling and
rebuying on day 1, which the cooldown forbids; the real answer is 2 as well, by
holding through. On `[1, 2, 4]` greedy says 3 and holding says 3 too, but on
`[1, 2, 1, 2]` greedy says 2 and the truth is 1. Greedy has no way to represent
"selling now costs me tomorrow".
""",
        ),
        (
            "The insight",
            """
Stop thinking about transactions and think about what state you are in at the
**close of each day**. There are exactly three:

- `hold` — you own a share.
- `sold` — you sold **today**, so tomorrow is a forced rest.
- `free` — you own nothing and are allowed to buy.

The transitions are the whole problem:

```
hold[i] = max(hold[i-1], free[i-1] - price)   # keep holding, or buy today
sold[i] = hold[i-1] + price                   # you can only sell what you held
free[i] = max(free[i-1], sold[i-1])           # yesterday's sale matures today
```

The cooldown never appears as a counter or a flag. It is encoded structurally:
there is **no edge from `sold` into `hold`**. A sale has to pass through `free`,
which takes one day, and that day is the cooldown.

Each row depends only on the previous one, so three integers replace three
arrays. The answer is `max(sold, free)` — ending while still holding a share is
never optimal.
""",
        ),
        (
            "The ordering trap, and initialisation",
            """
Every right-hand side above reads day `i-1`. Update the three variables in
place, one line at a time, and `hold` will read the `free` you *just* wrote —
that is the same-day path `free → hold → sold`, i.e. buying and selling on one
day with no cooldown, and it inflates the answer. Use a simultaneous tuple
assignment, or keep explicit `prev_*` copies.

Initialise `hold` and `sold` to a large negative sentinel, not to 0. `sold = 0`
on day 0 claims you sold something you never bought; it happens to be harmless
here because `free` is already 0, but the same shortcut in the fee variant
(where a sale subtracts the fee) is a real bug. Sentinels cost nothing.

Dry run `[1, 2, 3, 0, 2]`, tracking `(hold, sold, free)`:
`(-1, ·, 0) → (-1, 1, 0) → (-1, 2, 1) → (1, -1, 2) → (1, 3, 2)`. Answer **3**:
buy at 1, sell at 3, cooldown, buy at 0, sell at 2. The day-4 `hold = 1` is the
rebuy at price 0 funded by the `free = 1` that matured from the day-2 sale.
""",
        ),
    ],
}

_IMPOSSIBLE = -(10**9)  # cheaper than float("-inf") and keeps everything int


def max_profit(prices: list[int]) -> int:
    hold, sold, free = _IMPOSSIBLE, _IMPOSSIBLE, 0

    for price in prices:
        # Simultaneous: every right-hand side must read yesterday's values.
        hold, sold, free = (
            max(hold, free - price),  # keep holding, or buy out of `free`
            hold + price,  # sell today - only reachable from `hold`
            max(free, sold),  # yesterday's sale matures into `free`
        )

    return max(sold, free)  # never finish still holding


CASES = [
    (([1, 2, 3, 0, 2],), 3),
    (([1, 2, 1, 2],), 1),
    (([6, 1, 3, 2, 4, 7],), 6),
    (([1, 2, 4],), 3),
    (([5, 4, 3, 2, 1],), 0),
    (([2, 1],), 0),
    (([1],), 0),
    (([],), 0),
]


def solve(prices: list[int]) -> int:
    return max_profit(prices)
