"""Coin Change II — LeetCode 518."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Coin loop outside, amount loop inside — that order is the whole problem, because it counts combinations rather than orderings.",
    "time": "O(amount · coins)",
    "space": "O(amount)",
    "sections": [
        (
            "What it asks",
            """
Count the **combinations** of coins that sum to `amount`, with an unlimited
supply of each denomination. `1+1+2` and `2+1+1` are the same combination and
must be counted once.

Ask: combinations or permutations (combinations — and if the answer is
permutations you are writing Combination Sum IV instead, with the loops
swapped); is the supply unlimited (yes, so this is the *complete* knapsack,
not 0/1); can `amount` be 0 (yes, and the answer is 1 — the empty selection);
can the coin list be empty (yes).
""",
        ),
        (
            "Brute force, and the number",
            """
Recursing on "take this coin again, or move on to the next denomination"
enumerates every combination, and there is no early exit — you cannot prune a
counting problem. At `amount = 5000` with just three coins, `[1, 2, 5]`, there
are **1 252 001** combinations, so the tree has that many leaves at depths of
up to 5000: order 10⁹ steps for the easiest possible input, and it is
exponential in the number of denominations.

Memoising that recursion on `(index, remaining)` is already the right answer —
O(amount × coins) states, which at the stated limits is 5000 × 300 = 1.5·10⁶.
The array version below is the same table, filled iteratively.
""",
        ),
        (
            "State",
            """
> `dp[a]` = the number of combinations summing to exactly `a`, **using only
> the coins processed so far**.

That second clause is the entire difference from Coin Change I. It is not a
property you can read off the array — it is enforced by the loop order, which
is why the order is the answer and not a detail.

`dp[0] = 1`: there is exactly one way to make nothing, by taking nothing. Not
zero. Every entry in the table is ultimately built from that 1, so seeding it
wrong returns 0 everywhere.
""",
        ),
        (
            "Why the coin loop must be outside",
            """
```python
for coin in coins:               # outer: fixes an order on the denominations
    for target in range(coin, amount + 1):
        dp[target] += dp[target - coin]
```

Processing coins one at a time means every combination is counted in exactly
one canonical order — non-decreasing by denomination — so `1+1+2` is reached
once and `2+1+1` is never reached at all.

Swap the loops and you count **orderings**: on `amount = 5, coins = [1,2,5]`
the correct answer is **4** (`5`, `1+1+1+2`, `1+2+2`, `1+1+1+1+1`), and the
swapped version returns **9**. That is not a rounding error, it is a different
problem — and it is the same code, which is what makes it a good interview
question.

The inner loop runs **upwards**, from `coin` to `amount`. That is deliberate:
`dp[target - coin]` has already been updated with this same coin, so the coin
is reused, which is exactly what unlimited supply means. Compare with the 0/1
knapsack, where the inner loop runs downwards for precisely the opposite
reason. Being able to state that contrast in one sentence is what separates
"I remember this" from "I can derive this".

Starting the loop at `coin` also removes the bounds check — a coin larger than
`amount` runs zero iterations.
""",
        ),
        (
            "Dry run",
            """
`amount = 5`, `coins = [1, 2, 5]`. Start `dp = [1, 0, 0, 0, 0, 0]`.

After the coin **1** — one way to make each amount, all ones:

```
[1, 1, 1, 1, 1, 1]
```

After the coin **2**, each `dp[a] += dp[a-2]`:

```
[1, 1, 2, 2, 3, 3]
```

`dp[4] = 3` is `1+1+1+1`, `1+1+2`, `2+2`. Note that `2+1+1` never appears.

After the coin **5**, `dp[5] += dp[0]`:

```
[1, 1, 2, 2, 3, 4]
```

**4**. The single step where `dp[5]` gains the `1` seeded at `dp[0]` is the
one that shows why `dp[0] = 1` matters.
""",
        ),
        (
            "Follow-ups",
            """
- **Combination Sum IV** (LC 377) counts orderings — same two loops, swapped,
  with the amount outside. Interviewers pair these deliberately.
- **Bounded supply**, `k` of each coin: this becomes a bounded knapsack. The
  clean answer is binary splitting of the counts (1, 2, 4, … of each coin,
  each treated as a 0/1 item) for O(amount · Σ log kᵢ), or a monotonic-deque
  optimisation for O(amount · coins).
- **Which coins, not how many ways** — that is Coin Change I with a parent
  array.
- **Overflow.** The count fits in a signed 32-bit int by problem guarantee, but
  intermediate sums in other languages are worth a sentence.
- **Space.** O(amount), and the 2-D `dp[i][a]` table is only needed if you must
  reconstruct combinations; the fold is safe because each coin reads a row it
  is simultaneously writing, which is the reuse you want.
""",
        ),
    ],
}


def change(amount: int, coins: list[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1  # one way to make nothing: take nothing

    for coin in coins:
        # Coin outer + target ascending: combinations, with reuse allowed.
        for target in range(coin, amount + 1):
            dp[target] += dp[target - coin]

    return dp[amount]


CASES = [
    ((5, [1, 2, 5]), 4),  # swapping the loops gives 9
    ((4, [1, 2]), 3),  # ... and 5 here
    ((3, [2]), 0),
    ((10, [10]), 1),
    ((0, [7]), 1),  # the empty selection
    ((0, []), 1),
    ((3, []), 0),
    ((100, [1, 5, 10, 25]), 242),  # ways to make a dollar
]


def solve(amount: int, coins: list[int]) -> int:
    return change(amount, coins)
