"""Shortest Path in Binary Matrix — LeetCode 1091."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Eight-directional unweighted BFS; the only real decisions are marking visited on push and checking both endpoints first.",
    "time": "O(n²)",
    "space": "O(n²)",
    "sections": [
        (
            "What it asks",
            """
An `n × n` binary grid. Walk from `(0, 0)` to `(n-1, n-1)` over `0` cells
only, moving in any of the **eight** directions. Return the number of cells on
the shortest such path, or −1.

Two things to pin down before coding, because both change the answer by one or
by everything: the result counts **cells, not steps** (so a 1×1 open grid is
1, not 0), and diagonals are legal (so the Manhattan intuition is wrong — the
distance metric here is Chebyshev).
""",
        ),
        (
            "The insight",
            """
Every move costs the same, so BFS from the start gives the shortest path and
there is nothing to optimise about the algorithm itself. The interest is in
the bookkeeping.

Because eight neighbours means every cell is reachable from up to eight
predecessors, the frontier overlaps heavily: at n = 100 a lazy implementation
that marks visited **on pop** can push the same cell eight times before it is
ever popped, and the queue balloons. Mark on **push** — the moment you enqueue
a cell, it is claimed. In BFS this loses nothing, because the first time a
cell is enqueued is already along a shortest path to it.

Mutating the grid (`grid[r][c] = 1`) is the cheapest visited set here and
costs no extra memory, at the price of destroying the input — fine in an
interview if you say it, which is why `solve` copies before calling.
""",
        ),
        (
            "Edge cases",
            """
- **Start or end blocked** → −1 immediately. Checking only the start is the
  usual bug; a blocked `(n-1, n-1)` otherwise drains the whole queue and still
  returns −1, so it is not wrong, merely wasteful — but a blocked start pushed
  into the queue *is* wrong.
- **n = 1**: `[[0]]` → 1 and `[[1]]` → −1. The 1 catches anyone who returns a
  step count.
- **Fully open grid** → `n`, taken straight down the diagonal.
- `[[0,0],[1,1]]` → −1: the goal is a wall even though the start is fine.

Follow-up: **A\\*** with the Chebyshev heuristic `max(|dr|, |dc|)`, which is
admissible here and is exactly why the interviewer chose eight-directional
movement. Same worst case, far better typical case. And if cells had weights,
BFS breaks and it becomes Dijkstra — or 0-1 BFS with a deque if the weights
are only 0 and 1.
""",
        ),
    ],
}

DIRECTIONS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def shortest_path_binary_matrix(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return -1

    n = len(grid)
    if grid[0][0] == 1 or grid[n - 1][n - 1] == 1:
        return -1  # both ends, not just the start

    queue: deque[tuple[int, int, int]] = deque([(0, 0, 1)])  # cells, not steps
    grid[0][0] = 1  # claimed on push

    while queue:
        r, c, length = queue.popleft()
        if r == n - 1 and c == n - 1:
            return length
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                grid[nr][nc] = 1
                queue.append((nr, nc, length + 1))

    return -1


CASES = [
    (([[0, 1], [1, 0]],), 2),
    (([[0, 0, 0], [1, 1, 0], [1, 1, 0]],), 4),
    (([[1, 0, 0], [1, 1, 0], [1, 1, 0]],), -1),  # start blocked
    (([[0, 0], [1, 1]],), -1),  # goal blocked
    (([[0]],), 1),  # cells, not steps
    (([[1]],), -1),
    (([[0, 0, 0], [0, 1, 0], [0, 0, 0]],), 4),  # the diagonal is blocked, so 4 not 3
    (([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],), 4),  # the diagonal
]


def solve(grid: list[list[int]]) -> int:
    return shortest_path_binary_matrix([row[:] for row in grid])
