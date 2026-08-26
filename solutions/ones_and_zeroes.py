"""Ones and Zeroes — LeetCode 474."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "One 0/1 knapsack with two capacities: the item is a string, its weight is the pair (zeros, ones), and its value is 1.",
    "time": "O(len(strs) · m · n)",
    "space": "O(m · n)",
    "sections": [
        (
            "What it asks",
            """
Given binary strings and budgets of `m` zeros and `n` ones, take as many
strings as possible without exceeding either budget.

Ask: **can a string be taken twice?** No — each is a distinct item, which is
what makes this 0/1 rather than unbounded. Ask whether duplicate strings can
appear in the list (they can, and they are separate items). Confirm the
objective is the **count** of strings, not their total length: the value of
every item is 1, and that is why the greedy below is tempting.
""",
        ),
        (
            "The insight",
            """
Every item has value 1, so "as many as possible" invites a greedy: sort by
length, take what fits. With **one** budget that greedy is provably optimal —
cheapest-first maximises the count, and the exchange argument is one line.

Here the cost is a **vector**, `(zeros, ones)`, and there is no single scalar
to sort by. A string that is cheap overall can be the one that exhausts the
scarce dimension, and the exchange argument collapses: swapping a taken item
for an untaken one can free zeros while costing ones. Two-dimensional
knapsack with unit values is NP-hard in general; what rescues this problem is
that both budgets are tiny (≤ 100), so the whole state space fits in a table.

So it is a knapsack, with the only twist being two capacity dimensions:

> `dp[i][j]` = the most strings selectable using at most `i` zeros and `j`
> ones.

For each string with `z` zeros and `o` ones, `dp[i][j] = max(dp[i][j],
dp[i-z][j-o] + 1)`. The item loop is outermost; the two capacity loops are
inner. That is the same shape as a one-dimensional knapsack with the capacity
axis split in two — recognising it as *one* knapsack, not a new problem, is
the whole answer.
""",
        ),
        (
            "The loop order that decides it",
            """
Both capacity loops must run **downwards**, `i` from `m` to `z` and `j` from
`n` to `o`.

Running them upwards reads `dp[i-z][j-o]` *after* this same string has already
updated it, so the string gets taken repeatedly and you have silently solved
the unbounded knapsack. On `["10"], m = 5, n = 5` the correct answer is 1;
ascending loops return 5. This is the single bug that appears in this problem,
and it appears every time, because the code otherwise looks identical.

Two details worth stating:

- The loop bounds `range(m, z - 1, -1)` also serve as the "does it fit" test —
  no `if` needed, and a string that cannot fit at all runs zero iterations.
- Space is O(m·n) = at most 101 × 101, independent of the input size. Time is
  O(600 · 100 · 100) = 6 × 10⁶ at the stated limits — comfortable, and worth
  quoting so the interviewer knows you checked rather than hoped.
""",
        ),
    ],
}


def find_max_form(strs: list[str], m: int, n: int) -> int:
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for word in strs:
        zeros = word.count("0")
        ones = len(word) - zeros
        # Both descending: each string is used at most once (0/1, not unbounded).
        for i in range(m, zeros - 1, -1):
            for j in range(n, ones - 1, -1):
                dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)

    return dp[m][n]


CASES = [
    ((["10", "0001", "111001", "1", "0"], 5, 3), 4),
    ((["10", "0", "1"], 1, 1), 2),
    ((["10"], 5, 5), 1),  # ascending loops would say 5
    (([], 5, 5), 0),
    ((["111", "1111"], 0, 4), 1),  # zero budget of zeros
    ((["00", "000"], 3, 0), 1),
    ((["11", "1", "1", "0"], 1, 2), 3),
    ((["1", "1", "1"], 0, 0), 0),
]


def solve(strs: list[str], m: int, n: int) -> int:
    return find_max_form(strs, m, n)
