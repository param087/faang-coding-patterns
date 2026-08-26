"""Max Area of Island — LeetCode 695."""

from __future__ import annotations

META = {
    "pattern": "graph-traversal",
    "insight": "Number of Islands with a counter: each flood returns how many cells it swallowed, and you keep the largest.",
    "time": "O(rows · cols) — every cell is sunk once",
    "space": "O(rows · cols) worst case for the stack",
    "sections": [
        (
            "What it asks",
            """
Return the size of the largest 4-directionally connected region of `1`s. Zero
if there is no land at all.

Ask: are entries integers or characters (integers here, unlike Number of
Islands — the same code with `== "1"` silently returns 0); is the grid
guaranteed non-empty; may I mutate it.
""",
        ),
        (
            "The insight",
            """
Identical traversal to Number of Islands, except each flood reports its own
size instead of just incrementing a counter. Every land cell belongs to exactly
one region, so the total work across all floods is still one pass over the
grid.

Sinking visited land to `0` is what keeps it linear: without marking, the four
neighbours of every cell re-enter each other's traversals and the same region
is walked repeatedly.

The counting is easiest to get right iteratively — `area += 1` on pop, once per
cell, because a cell is pushed exactly once. The recursive form
(`1 + dfs(up) + dfs(down) + ...`) is equivalent but people routinely forget the
leading `1` or return before recursing on all four directions.
""",
        ),
        (
            "Edge cases",
            """
- **No land at all** → 0, not `-inf`. Seed `best = 0`, do not seed it from the
  first flood.
- **Empty grid or empty first row** — `len(grid[0])` on `[]` throws.
- **Diagonally touching cells are separate islands.** `[[1,0],[0,1]]` is two
  islands of area 1, so the answer is 1 and not 2. If the interviewer wants
  8-way connectivity, only the direction tuple changes.
- **Depth.** A 50×50 grid of solid land recurses 2,500 frames deep; at the
  300×300 sizes interviewers like, recursion is 90,000 frames and Python's
  default limit is 1,000. The explicit stack costs three lines.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def max_area_of_island(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    best = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1:
                continue

            area = 0
            grid[r][c] = 0
            stack = [(r, c)]
            while stack:
                cr, cc = stack.pop()
                area += 1  # counted on pop, but each cell is pushed only once
                for dr, dc in DIRECTIONS:
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                        grid[nr][nc] = 0  # mark on push
                        stack.append((nr, nc))

            best = max(best, area)

    return best


CASES = [
    (
        (
            [
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 1, 0],
                [0, 1, 0, 0, 1, 1],
                [0, 1, 0, 0, 1, 0],
            ],
        ),
        4,
    ),
    (([[0, 0, 0], [0, 0, 0]],), 0),
    (([[1, 1, 1], [1, 1, 1], [1, 1, 1]],), 9),
    (([[1, 0], [0, 1]],), 1),  # diagonals do not connect
    (([[1]],), 1),
    (([[1, 1], [1, 1]],), 4),  # 4, not 8: marking on push stops double counting
    (([],), 0),
]


def solve(grid: list[list[int]]) -> int:
    # Copy: max_area_of_island sinks the grid, and CASES are reused across runs.
    return max_area_of_island([row[:] for row in grid])
