"""Number of Islands — LeetCode 200."""

from __future__ import annotations

META = {
    "pattern": "graph-traversal",
    "insight": "Every unvisited land cell starts exactly one island; flood it and count the floods.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols) worst case for the stack",
    "sections": [
        (
            "What it asks",
            """
Count connected regions of `'1'` in a grid of `'1'` and `'0'`.

Ask: are diagonals connected (usually not — but ask, it changes the direction
list); may I modify the grid; can the grid be empty; are the entries characters
or integers (characters on LeetCode, which catches people comparing to `0`).
""",
        ),
        (
            "The insight",
            """
Every unvisited land cell begins exactly one island. Flood-fill from it, and
everything reachable belongs to that same island. The number of flood-fills is
the answer.

BFS or DFS both work, because you only need connectivity, not distance. DFS is
shorter — but see below.
""",
        ),
        (
            "Write it iteratively",
            """
A 300×300 grid of all land recurses 90,000 deep and blows Python's 1000-frame
limit. Interviewers, at Google especially, will hand you exactly that input.

An explicit stack costs three extra lines and removes the failure mode. Say
why you are doing it.
""",
        ),
        (
            "Mark on push, not on pop",
            """
If a cell is only marked when it is dequeued, the same cell can be queued many
times before it is first processed, and the frontier blows up.

Marking at push time is the general BFS/DFS rule and it is the most common
performance bug in grid problems.
""",
        ),
        (
            "The sinking trade-off",
            """
Overwriting `'1'` with `'0'` avoids a separate `visited` set — O(1) extra
space instead of O(rows·cols).

It also **mutates the caller's grid**. Say that you are doing it and offer the
`visited` set instead; some interviewers care a great deal, and volunteering
the trade-off is better than being caught by it.
""",
        ),
        (
            "Follow-ups",
            """
- **"The grid arrives as a stream of add-land operations, and you must report
  the island count after each."** That is [Union-Find](../../patterns/union-find/) —
  connectivity is now growing over time, and the answer changes entirely.
- **Max Area of Island** — return the size of the largest flood rather than
  the count.
- **Number of Distinct Islands** — canonicalise each island's shape relative
  to its starting cell and count distinct shapes.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def num_islands(grid: list[list[str]]) -> int:
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def sink(start_r: int, start_c: int) -> None:
        # Iterative: a 300x300 grid of land would overflow the call stack.
        stack = [(start_r, start_c)]
        grid[start_r][start_c] = "0"
        while stack:
            r, c = stack.pop()
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                    grid[nr][nc] = "0"  # mark on push, not on pop
                    stack.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)

    return count


CASES = [
    (
        (
            [
                ["1", "1", "0", "0", "0"],
                ["1", "1", "0", "0", "0"],
                ["0", "0", "1", "0", "0"],
                ["0", "0", "0", "1", "1"],
            ],
        ),
        3,
    ),
    (([["1", "1"], ["1", "1"]],), 1),
    (([["1", "0"], ["0", "1"]],), 2),
    (([["0"]],), 0),
    (([],), 0),
]


def solve(grid: list[list[str]]) -> int:
    # Copy: num_islands sinks the grid, and CASES are reused across runs.
    return num_islands([row[:] for row in grid] if grid else grid)
