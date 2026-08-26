"""Triangle — LeetCode 120."""

from __future__ import annotations

META = {
    "pattern": "dp-grid-knapsack",
    "insight": "Sweep bottom-up and every cell has exactly two children, so there are no boundary cases and the answer lands on the apex.",
    "time": "O(n²) for n rows",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Row `r` has `r + 1` entries; from index `i` you may step to `i` or `i + 1` in
the next row. Minimise the sum along a top-to-bottom path.

Ask: **can the values be negative?** Yes (−10⁴ to 10⁴), which kills any
"always take the smaller child" shortcut and is worth stating out loud. Also
ask whether the triangle can be a single row (yes, answer is that element).
""",
        ),
        (
            "The insight",
            """
The natural direction is top-down, and it is the worse one. Going down, index
`i` in row `r` is reachable from `i - 1` and `i`, and both of those may not
exist — the first and last entry of each row need special handling, and you
still have to `min` over the final row at the end.

Turn it around:

> `dp[i]` = the cheapest path from row `r`, index `i`, down to the bottom.

Sweeping upwards, `dp[i] = row[i] + min(dp[i], dp[i+1])`, and **both children
always exist** because row `r + 1` is exactly one longer than row `r`. No
boundary branches, and the answer is `dp[0]` rather than a min over a row.
That is the whole trick, and it generalises: when one direction of a DP has
ragged boundaries, check the other.

Greedy is the wrong first answer. On

```
   1
  2 3
100 100 1
```

taking the cheaper child gives `1 → 2 → 100` = 103; the optimum is
`1 → 3 → 1` = **5**. Have that ready.
""",
        ),
        (
            "Follow-ups",
            """
- **O(n) extra space** is what the problem asks for as a bonus, and the
  bottom-up sweep gives it for free: one array the width of the last row,
  overwritten in place, left to right. In-place *inside the triangle* is O(1)
  extra but mutates the input — offer it, do not assume it is wanted.
- **Reconstruct the path.** Keep the choice made at each cell, or re-walk from
  the apex afterwards comparing `dp` values; the bottom-up table makes the
  re-walk trivial.
- **Maximum instead of minimum** — swap `min` for `max`. Because values can be
  negative, no sign trick is needed either way.
- **Why not Dijkstra?** It works, but the graph is a DAG in topological order
  already, so the heap buys nothing: O(n² log n) instead of O(n²).
""",
        ),
    ],
}


def minimum_total(triangle: list[list[int]]) -> int:
    if not triangle:
        return 0

    dp = list(triangle[-1])  # copy: the caller's triangle stays untouched

    for row in reversed(triangle[:-1]):
        for i, value in enumerate(row):
            # Both children exist — the row below is exactly one wider.
            dp[i] = value + min(dp[i], dp[i + 1])

    return dp[0]


CASES = [
    (([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]],), 11),
    (([[1], [2, 3], [100, 100, 1]],), 5),  # greedy from the top says 103
    (([[-10]],), -10),
    (([[-1], [2, 3], [1, -1, -3]],), -1),
    (([[1], [2, 3]],), 3),
    (([[1], [1, 1], [1, 1, 1]],), 3),
    (([],), 0),
]


def solve(triangle: list[list[int]]) -> int:
    return minimum_total(triangle)
