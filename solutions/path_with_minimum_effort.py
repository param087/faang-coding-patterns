"""Path With Minimum Effort — LeetCode 1631."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "binary-search-answer",
    "insight": "The cost of a path is a max, not a sum, so fix a threshold, delete every edge above it, and ask only whether the corner is reachable.",
    "time": "O(m·n·log(max height difference))",
    "space": "O(m·n)",
    "sections": [
        (
            "What it asks",
            """
On an `m × n` grid of heights, walk from the top-left cell to the bottom-right
using 4-directional moves. A route's **effort** is the largest absolute height
difference between any two consecutive cells on it — not the total, the
maximum. Return the smallest effort achievable.

Ask whether the grid can be `1 × 1` (it can, and the answer is 0, which several
otherwise-correct implementations return as `inf`). Ask whether diagonals count
(no). And confirm out loud that the cost is a **max over edges**: that single
word is what makes the whole problem tractable and it is easy to skim past.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Enumerate paths and take the best. On a 100 × 100 grid the number of monotone
(right/down only) paths alone is C(198, 99) ≈ 2 × 10⁵⁸ — and the real problem
allows backtracking upwards and leftwards, so it is worse than that.

DP does not rescue it either. `dp[r][c] = min effort to reach here` is not
computable in a single row-major pass, because the optimal route to a cell can
arrive from below or from the right. Say this before you reach for Dijkstra;
"the DP has cycles" is the honest reason a graph algorithm is needed.
""",
        ),
        (
            "The insight",
            """
Because the cost is a **max**, the question "is there a path of effort `<= t`?"
does not care about anything except which edges survive. Delete every edge
whose height difference exceeds `t` and the whole problem collapses to plain
reachability — a BFS or a DFS, no priorities, no distances.

And that predicate is monotone: if a path exists under threshold `t`, the same
path exists under `t + 1`. So the feasible thresholds are a suffix of the
range, and you binary search for where the suffix starts.

That is the entire trick. Twenty-odd BFS runs, each O(m·n), where an unguided
search would have gone exponential. The general lesson: when an objective is a
bottleneck (a min-of-max or max-of-min) rather than a sum, thresholding turns
optimisation into connectivity.
""",
        ),
        (
            "Bounds, and the two details that decide it",
            """
Low is **0**, not 1. A flat grid has effort 0, and starting at 1 quietly
returns 1 for `[[1,1],[1,1]]`. High is `max(heights) - min(heights)`, which
always admits a path (every edge survives); `10**6` also works since heights
are bounded, but the tighter bound is free and shows you thought about it.

The other detail is **where `visited` is marked**. Mark a cell when you push
it, not when you pop it. Marking on pop lets the same cell sit in the queue
several times, and on a 100 × 100 grid with many equal heights the frontier
blows up — the search stops being O(m·n) per threshold and the twenty BFS runs
stop being cheap.

Also note the search never mutates `heights`; the visited set is a separate
2-D array of booleans, so the same grid can be re-tested at every threshold.
""",
        ),
        (
            "Dry run",
            """
```
1 2 2
3 8 2
5 3 5
```

- `low = 0`, `high = 8 - 1 = 7`.
- `t = 3`: reachable — go `1 → 3 → 5 → 3 → 5`, whose worst step is 2. Feasible,
  so `high = 3`.
- `t = 1`: from `1` you may step to `2` (diff 1) and on to `2` (diff 0), then
  you are stuck: `2 → 8` is 6, `2 → 3` is 1 but from `3` the only exits are
  `1` (visited) and `5` (diff 2) and `8`. The corner never gets reached.
  Infeasible, `low = 2`.
- `t = 2`: `1 → 2 → 2 → 2 → 5`, worst step 2 at the end. Feasible, `high = 2`.

Answer **2**. Notice that the greedy "always step to the nearest height" route
`1 → 2 → 2 → 2 → 5` and the route down the left edge both cost 2, but a plain
row-major DP that only looks up and left computes 3 — that is the case that
catches the DP.
""",
        ),
        (
            "Follow-ups",
            """
- **"Can you do it without the log factor?"** Yes, twice over. Dijkstra with
  `dist[cell] = min over paths of the max edge` and relaxation
  `max(d, |Δh|)` runs in O(m·n·log(m·n)). Or sort all `2·m·n` edges by weight
  and union them in ascending order until the two corners share a component —
  Kruskal, and the answer is the weight of the edge that joined them. The
  union-find version is the fastest and is what you write if asked to handle
  many queries on the same grid.
- **"Now the cost is the sum of differences."** Thresholding dies instantly —
  a sum is not monotone under edge deletion in the same way. That is plain
  Dijkstra, and being able to say *why* the threshold trick stops applying is
  the point of the follow-up.
- Same shape as **Swim in Rising Water** (778) and **Minimum Effort Path**
  variants: bottleneck objective → binary search plus reachability.
""",
        ),
    ],
}


def minimum_effort_path(heights: list[list[int]]) -> int:
    rows, cols = len(heights), len(heights[0])

    def reachable(limit: int) -> bool:
        seen = [[False] * cols for _ in range(rows)]
        seen[0][0] = True
        queue = deque([(0, 0)])
        while queue:
            row, col = queue.popleft()
            if row == rows - 1 and col == cols - 1:
                return True
            for next_row, next_col in (
                (row + 1, col),
                (row - 1, col),
                (row, col + 1),
                (row, col - 1),
            ):
                if not (0 <= next_row < rows and 0 <= next_col < cols):
                    continue
                if seen[next_row][next_col]:
                    continue
                if abs(heights[next_row][next_col] - heights[row][col]) <= limit:
                    seen[next_row][next_col] = True  # mark on push, not on pop
                    queue.append((next_row, next_col))
        return False

    flat = [h for row in heights for h in row]
    low, high = 0, max(flat) - min(flat)  # 0 is reachable on a flat grid
    while low < high:
        mid = (low + high) // 2
        if reachable(mid):
            high = mid
        else:
            low = mid + 1

    return low


CASES = [
    (([[1, 2, 2], [3, 8, 2], [5, 3, 5]],), 2),
    (([[1, 2, 3], [3, 8, 4], [5, 3, 5]],), 1),
    (
        (
            [
                [1, 2, 1, 1, 1],
                [1, 2, 1, 2, 1],
                [1, 2, 1, 2, 1],
                [1, 2, 1, 2, 1],
                [1, 1, 1, 2, 1],
            ],
        ),
        0,
    ),
    (([[3, 2, 1], [1, 1, 1], [1, 1, 1]],), 1),
    (([[1]],), 0),
    (([[1, 10]],), 9),
    (([[1], [1000000]],), 999999),
]


def solve(heights: list[list[int]]) -> int:
    return minimum_effort_path([row[:] for row in heights])
