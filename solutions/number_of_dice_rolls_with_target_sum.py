"""Number of Dice Rolls With Target Sum — LeetCode 1155."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Adding one die shifts the whole distribution by 1..k, so each new row is k overlapping copies of the previous one summed together.",
    "time": "O(n · target · k), or O(n · target) with a prefix sum",
    "space": "O(target)",
    "sections": [
        (
            "What it asks",
            """
Roll `n` dice, each with faces `1…k`. Count the ordered outcomes whose pips sum
to `target`, modulo 1e9+7.

Ask whether the dice are **distinguishable** — they are, `(1,2)` and `(2,1)` are
two outcomes, which is why this is a plain count and not a partition problem.
Note the constraints: `n, k ≤ 30`, `target ≤ 1000`, so the table is at most
30 × 1000 and there is no need to be clever.
""",
        ),
        (
            "The insight",
            """
This is a bounded knapsack where every item must be taken exactly once and its
"weight" is a free choice in `1…k`.

> `dp[d][t]` = the number of ways the first `d` dice sum to exactly `t`.

Condition on the **last** die: it shows some face `f`, and the rest must have
made `t - f`.

```
dp[d][t] = Σ_{f = 1..k} dp[d-1][t-f]
```

with `dp[0][0] = 1` — one way to roll nothing and score nothing. That empty-sum
base case is doing real work; seeding `dp[1][f] = 1` by hand is where off-by-one
bugs come from.

Only the previous row is ever read, so keep one array of length `target + 1`
and rebuild it per die. `n · target · k` is 900 000 at the limits.

Two free rejections before any allocation: `target < n` (impossible, every die
shows at least 1) and `target > n * k` (impossible, every die shows at most `k`).
""",
        ),
        (
            "Follow-ups",
            """
- **Drop the `k` factor.** The inner sum is a sliding window over a contiguous
  block of the previous row, so a prefix-sum array turns each entry into
  `pre[t] - pre[t-k]` and the whole thing into O(n · target). Interviewers who
  ask "can you do better than `n·target·k`?" want exactly this.
- **Closed form.** Inclusion–exclusion gives
  `Σ_j (-1)^j · C(n, j) · C(target - jk - 1, n - 1)` — worth naming, not worth
  writing under time pressure.
- **Dice of differing face counts** — the recurrence is unchanged, just use each
  die's own `k` per row. The prefix-sum trick still applies per row.
- The identical skeleton counts strings, coin combinations with a fixed number
  of coins, and any "exactly `n` choices summing to `t`" question.
""",
        ),
    ],
}

MOD = 10**9 + 7


def num_rolls_to_target(n: int, k: int, target: int) -> int:
    if target < n or target > n * k:
        return 0  # unreachable by the pip bounds alone

    dp = [0] * (target + 1)
    dp[0] = 1  # one way to roll zero dice for a sum of zero

    for _ in range(n):
        nxt = [0] * (target + 1)
        for total in range(1, target + 1):
            # Faces 1..k land on dp[total-k .. total-1], clamped at zero.
            nxt[total] = sum(dp[max(0, total - k) : total]) % MOD
        dp = nxt

    return dp[target]


def num_rolls_to_target_prefix(n: int, k: int, target: int) -> int:
    """Same recurrence, with the inner window replaced by a prefix sum."""
    if target < n or target > n * k:
        return 0

    dp = [0] * (target + 1)
    dp[0] = 1

    for _ in range(n):
        prefix = [0] * (target + 2)
        for total in range(target + 1):
            prefix[total + 1] = (prefix[total] + dp[total]) % MOD
        dp = [
            (prefix[total] - prefix[max(0, total - k)]) % MOD if total else 0
            for total in range(target + 1)
        ]

    return dp[target]


CASES = [
    ((1, 6, 3), 1),
    ((2, 6, 7), 6),
    ((30, 30, 500), 222616187),  # forces the modulo to be real
    ((1, 6, 7), 0),  # above n*k
    ((2, 5, 1), 0),  # below n
    ((3, 2, 7), 0),
    ((3, 2, 6), 1),  # only every die showing its top face
    ((5, 4, 10), 101),
]


def solve(n: int, k: int, target: int) -> int:
    return num_rolls_to_target(n, k, target)


def check() -> None:
    for args, expected in CASES:
        assert num_rolls_to_target(*args) == expected, args
        # The O(n·target) variant must agree everywhere.
        assert num_rolls_to_target_prefix(*args) == expected, args
