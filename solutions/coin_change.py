"""Coin Change — LeetCode 322."""

from __future__ import annotations

META = {
    "pattern": "dp-1d",
    "insight": "Greedy fails on [1,3,4] making 6 — so build up the fewest coins for every amount below the target.",
    "time": "O(amount · coins)",
    "space": "O(amount)",
    "sections": [
        (
            "What it asks",
            """
Fewest coins summing to exactly `amount`, or −1 if impossible. Unlimited
supply of each denomination.

Ask: fewest coins, or number of ways (different problems — Coin Change II is
the counting one); is the supply unlimited (yes); can the amount be zero (yes,
answer 0); are the denominations arbitrary (yes, and that is what kills
greedy).
""",
        ),
        (
            "Why greedy fails",
            """
Have the counterexample ready before they ask. It is the strongest thing you
can do on this problem, because it proves you are reasoning rather than
recalling.

Coins `[1, 3, 4]`, amount **6**:

- Greedy takes the largest first: 4, then 1, then 1 → **three coins**.
- Optimal is 3 + 3 → **two coins**.

Greedy works for real currency systems because they are designed to be
canonical. Arbitrary denominations are not.
""",
        ),
        (
            "State first",
            """
> `dp[a]` = the fewest coins summing to exactly `a`.

Say that sentence before writing anything. Most failed DP is a state failure,
not a coding one.

The recurrence follows immediately: to make `a`, use some coin `c` and add one
to whatever `dp[a - c]` was.
""",
        ),
        (
            "The sentinel",
            """
`amount + 1` stands in for infinity — it is strictly larger than any real
answer (which is at most `amount`, all ones), so `min` never picks it, and the
final check maps it to −1.

Using `float('inf')` also works and keeps the intent obvious. Using `-1` as
the sentinel does not, because `min` would happily choose it.
""",
        ),
        (
            "Complexity, precisely",
            """
O(amount × len(coins)).

Note this is **pseudo-polynomial** — linear in the *magnitude* of the amount,
not in its number of digits. Saying that is a nice piece of precision, and it
is the reason the problem caps the amount at 10⁴.
""",
        ),
        (
            "Follow-ups",
            """
- **Coin Change II** — the number of combinations rather than the fewest
  coins. The recurrence sums instead of minimising, and the **loop order**
  decides whether you count combinations or permutations.
- **Reconstruct the actual coins** — keep a parent array recording which coin
  produced each amount.
- **Bounded supply** — becomes a 0/1 knapsack, and the inner loop reverses.
""",
        ),
    ],
}


def coin_change(coins: list[int], amount: int) -> int:
    unreachable = amount + 1  # strictly larger than any real answer
    dp = [unreachable] * (amount + 1)
    dp[0] = 0

    for target in range(1, amount + 1):
        for coin in coins:
            if coin <= target:
                dp[target] = min(dp[target], dp[target - coin] + 1)

    return -1 if dp[amount] == unreachable else dp[amount]


CASES = [
    (([1, 2, 5], 11), 3),
    (([2], 3), -1),
    (([1], 0), 0),
    (([1, 3, 4], 6), 2),  # the case greedy gets wrong
    (([2, 5, 10, 1], 27), 4),
    (([186, 419, 83, 408], 6249), 20),
]


def solve(coins: list[int], amount: int) -> int:
    return coin_change(coins, amount)
