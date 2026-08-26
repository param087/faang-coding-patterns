"""Minimum Cost to Make at Least One Valid Path in a Grid — LeetCode 1368."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "shortest-paths",
    "insight": "Every edge costs 0 (follow the arrow) or 1 (rewrite it), and a deque keeps that two-valued frontier sorted without a heap.",
    "time": "O(R · C)",
    "space": "O(R · C)",
    "sections": [
        (
            "What it asks",
            """
Each cell holds an arrow (1 right, 2 left, 3 down, 4 up). You may change any
cell's arrow at a cost of 1. Return the minimum total cost so that following
the arrows from the top-left leads to the bottom-right.

The framing to state immediately: you are **not** rerouting anything at
traversal time. You may walk from any cell to any of its four neighbours; the
walk is free in the arrow's own direction and costs 1 in the other three. So
the answer is the cheapest walk under that cost function — a shortest-path
problem, not a grid-DP problem.

Worth asking: can a cell be changed more than once (irrelevant — an optimal
path visits each cell at most once) and is the cost per changed cell or per
traversal (per cell, same thing here).
""",
        ),
        (
            "The insight",
            """
Weights are only ever 0 or 1, which is the special case where Dijkstra
collapses into **0-1 BFS**: a `deque` instead of a heap. A 0-cost move goes on
the **front**, a 1-cost move on the **back**.

That single rule keeps the deque sorted by distance with at most two distinct
values in it at any moment, which is precisely the invariant a priority queue
would maintain — for free. O(R · C) instead of O(R · C log(R · C)). At the
100 × 100 limit the log factor is about 13, so this is not about the runtime;
it is about knowing that a heap is unnecessary here.

The wrong first answer is plain BFS with a visited set. BFS minimises the
number of *cells stepped on*; the question asks for the number of arrows
rewritten, and those two objectives come apart the moment a free detour is
cheaper than a direct rewrite.

The other tempting wrong answer is DP over the grid. Movement here is not
monotone. On `[[3,1,3,4],[1,4,1,4]]` the free route is down, right, **up**,
right, down, right — cost **0**, while the best right/down-only route costs 1.
No sweep order makes a DP correct when the optimal path doubles back.
""",
        ),
        (
            "The pitfall: no visited set",
            """
The instinct carried over from BFS is to mark a cell visited when you first
reach it. Here that is wrong, because a cell can be reached later at a **lower**
cost via a chain of free moves that arrived from a different direction.

Relax on the distance instead: push whenever `d + cost < dist[next]`. A cell may
enter the deque more than once; the total work is still linear because each
improvement strictly lowers a bounded integer.

Two smaller details:

- Read `dist[r][c]` when you **pop**, not the value you stored when you pushed.
  The recorded distance only ever decreases, so reading it fresh is correct and
  saves carrying it through the deque.
- Direction indices are 1-based to match the arrow encoding. Enumerating
  `[(0,1), (0,-1), (1,0), (-1,0)]` from 1 lines up right/left/down/up with
  1/2/3/4 exactly; get that mapping wrong and the code still runs, just with a
  cost function that is off in two of four directions.
""",
        ),
    ],
}

# Index i (1-based) is the move for arrow value i: 1 right, 2 left, 3 down, 4 up.
DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))


def min_cost(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]
    dist[0][0] = 0

    queue = deque([(0, 0)])
    while queue:
        r, c = queue.popleft()
        d = dist[r][c]  # always current-best; it only ever decreases
        for arrow, (dr, dc) in enumerate(DIRECTIONS, start=1):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            cost = 0 if grid[r][c] == arrow else 1
            if dist[nr][nc] == -1 or d + cost < dist[nr][nc]:
                dist[nr][nc] = d + cost
                if cost == 0:
                    queue.appendleft((nr, nc))  # free move keeps the frontier sorted
                else:
                    queue.append((nr, nc))

    return dist[rows - 1][cols - 1]


CASES = [
    (([[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]],), 3),
    (([[1, 1, 3], [3, 2, 2], [1, 1, 4]],), 0),
    (([[1, 2], [4, 3]],), 1),
    (([[2, 2, 2], [2, 2, 2]],), 3),
    (([[4]],), 0),
    # Free the whole way down then right.
    (([[3, 3], [1, 1]],), 0),
    # The last arrow points out of the grid, so one rewrite is unavoidable.
    (([[1, 1], [1, 1]],), 1),
    # Start arrow points out of the grid.
    (([[2, 1, 1], [1, 1, 1], [1, 1, 1]],), 2),
    # Free route doubles back upwards; the best right/down-only route costs 1.
    (([[3, 1, 3, 4], [1, 4, 1, 4]],), 0),
    # Every arrow points the wrong way.
    (([[2, 2, 2], [2, 2, 2], [2, 2, 2]],), 4),
]


def solve(grid: list[list[int]]) -> int:
    return min_cost([row[:] for row in grid])
