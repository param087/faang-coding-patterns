"""Swim in Rising Water — LeetCode 778."""

from __future__ import annotations

META = {
    "pattern": "binary-search-answer",
    "insight": "Water level t makes every cell with grid[r][c] <= t passable, so the question is just: at which t do the two corners connect?",
    "time": "O(n² log(n²))",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
An `n × n` grid holds a permutation of `0 … n² - 1`; `grid[r][c]` is the
elevation of that cell. At time `t` the water level is `t`, and you may move
4-directionally between cells whose elevation is at most `t` — swimming is
instantaneous, so only the *waiting* costs anything. Return the earliest time
you can be at `(n-1, n-1)` having started at `(0, 0)`.

Ask whether the values are guaranteed to be a permutation (they are, which
bounds the answer by `n² - 1` and rules out ties). Ask whether you can move
back and forth freely (yes — swimming is free, so the route may wander).
""",
        ),
        (
            "The insight",
            """
The cost of a route is `max(elevation)` over its cells, a **bottleneck**, not a
sum. That is the signal to threshold.

Fix a time `t`. Every cell with `grid[r][c] <= t` is submerged and passable;
everything else is a wall. "Can I finish by time `t`?" is now plain
reachability — one DFS or BFS, no priority queue, no distances. And it is
monotone: the water only rises, so a cell that was passable at `t` is passable
at `t + 1` and any route that worked still works. Feasible times form a suffix.

Binary search that suffix. `log(n²)` reachability sweeps, each O(n²), and on
the maximum 50 × 50 grid that is about 11 sweeps of 2 500 cells — roughly
30 000 steps for a problem that looks like it needs a shortest path.
""",
        ),
        (
            "Bounds, and the alternatives you should name",
            """
Low is `max(grid[0][0], grid[n-1][n-1])` — you cannot leave the start or enter
the end before either is submerged. Starting at 0 still works but the tighter
bound is what makes the `1 × 1` case (`[[0]] → 0`) fall out for free. High is
`n² - 1`: at that time the whole grid is under water and the corners are
certainly connected.

Do not forget to test the start cell itself inside the check. A search that
seeds the frontier with `(0, 0)` unconditionally will report success at
`t = 0` on `[[3, 2], [0, 1]]`, because it never asked whether the start was
submerged. The tight lower bound also removes this, but relying on the bound
silently is not the same as knowing why.

Two other solutions are worth mentioning, because interviewers ask:

- **Dijkstra** on `dist[cell] = min over routes of max elevation`, relaxing
  with `max(d, grid[nr][nc])`. O(n² log n), one pass, no outer loop.
- **Union-find**: add cells in increasing elevation order and stop the moment
  the two corners share a component. Near-linear, and the natural answer if
  you are asked for the whole sequence of connection times.

The binary search is the one you can write correctly under pressure; say the
other two exist and why you did not pick them.
""",
        ),
    ],
}


def swim_in_water(grid: list[list[int]]) -> int:
    n = len(grid)

    def reachable(time: int) -> bool:
        if grid[0][0] > time:  # the start has to be submerged too
            return False
        seen = [[False] * n for _ in range(n)]
        seen[0][0] = True
        stack = [(0, 0)]
        while stack:
            row, col = stack.pop()
            if row == n - 1 and col == n - 1:
                return True
            for next_row, next_col in (
                (row + 1, col),
                (row - 1, col),
                (row, col + 1),
                (row, col - 1),
            ):
                if not (0 <= next_row < n and 0 <= next_col < n):
                    continue
                if seen[next_row][next_col] or grid[next_row][next_col] > time:
                    continue
                seen[next_row][next_col] = True
                stack.append((next_row, next_col))
        return False

    low, high = max(grid[0][0], grid[n - 1][n - 1]), n * n - 1
    while low < high:
        mid = (low + high) // 2
        if reachable(mid):
            high = mid
        else:
            low = mid + 1

    return low


CASES = [
    (([[0, 2], [1, 3]],), 3),
    (([[0, 3], [1, 2]],), 2),
    (([[3, 2], [0, 1]],), 3),
    (
        (
            [
                [0, 1, 2, 3, 4],
                [24, 23, 22, 21, 5],
                [12, 13, 14, 15, 16],
                [11, 17, 18, 19, 20],
                [10, 9, 8, 7, 6],
            ],
        ),
        16,
    ),
    (([[0, 1, 2], [3, 4, 5], [6, 7, 8]],), 8),
    (([[0]],), 0),
]


def solve(grid: list[list[int]]) -> int:
    return swim_in_water([row[:] for row in grid])
