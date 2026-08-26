"""Paint House — LeetCode 256."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Only the previous house's colour constrains the next one, so three running totals — best-ending-in-each-colour — carry all the history.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
*This one is premium, so here is the task in my own words rather than
LeetCode's text.* You are given an `n × 3` cost table: `costs[i][c]` is the
price of painting house `i` in colour `c` (red, blue or green). No two
**adjacent** houses may share a colour. Return the minimum total cost.

Ask whether the houses form a line or a **ring** — a ring is a genuinely
different problem (you would run the line DP three times, once per fixed colour
for house 0, and take the best). Ask whether `n` can be 0; return 0 if so.
""",
        ),
        (
            "The insight",
            """
The constraint is purely local: house `i` only cares about the colour of house
`i-1`. So the state is the colour you just used.

> `dp[i][c]` = cheapest way to paint houses `0…i` with house `i` in colour `c`.

```
dp[i][c] = costs[i][c] + min(dp[i-1][c'] for c' != c)
```

Only the previous row is ever read, so keep three scalars and rewrite them per
house. Python's simultaneous assignment evaluates the whole right-hand side
first, so all three updates see the *old* values — which is exactly what the
recurrence requires, and worth pointing at rather than leaving as luck.

O(n) time, O(1) space, one pass. The whole thing is four lines.
""",
        ),
        (
            "Follow-ups",
            """
- **Greedy is the wrong first answer.** "Pick the cheapest legal colour for each
  house in turn" fails on `[[1, 2, 3], [1, 100, 100]]`: greedy takes 1 for house
  0, is then barred from red and pays 100, total **101**. Paying 2 up front for
  house 0 lets house 1 take the 1, total **3**. A cheap local choice can cost 50×
  downstream — that is the sentence that earns the DP.
- **Paint House II** (LeetCode 265), `k` colours. The literal recurrence is
  O(n·k²). Track the **two smallest** values in the previous row instead: every
  colour uses the smallest unless it *is* the smallest, in which case it uses the
  runner-up. O(n·k). This is the actual interview question — expect it as the
  immediate follow-up.
- **Paint House III** (LeetCode 1473) adds a target neighbourhood count, so the
  state becomes `(house, colour, blocks so far)`.
- **Paint Fence** (276) is the same shape with "no *three* consecutive alike",
  which needs a same/different flag rather than the colour itself.
""",
        ),
    ],
}


def min_cost(costs: list[list[int]]) -> int:
    if not costs:
        return 0

    red, blue, green = costs[0]

    for r, b, g in costs[1:]:
        # Simultaneous assignment: every branch reads the previous house's row.
        red, blue, green = (
            r + min(blue, green),
            b + min(red, green),
            g + min(red, blue),
        )

    return min(red, blue, green)


CASES = [
    (([[17, 2, 17], [16, 16, 5], [14, 3, 19]],), 10),
    (([[1, 2, 3], [1, 100, 100]],), 3),  # greedy pays 101
    (([[7, 6, 2]],), 2),
    (([],), 0),
    (([[1, 2, 3], [1, 2, 3], [3, 2, 1]],), 4),
    (([[5, 8, 6], [19, 14, 13], [7, 5, 12], [14, 15, 17], [3, 20, 10]],), 43),
    (([[0, 0, 0], [0, 0, 0]],), 0),
]


def solve(costs: list[list[int]]) -> int:
    return min_cost([row[:] for row in costs])
