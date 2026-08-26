"""Longest Increasing Path in a Matrix — LeetCode 329."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "topological-sort",
    "insight": "Strictly increasing moves make the grid a DAG, so peel local minima layer by layer — the number of layers is the longest path.",
    "time": "O(m·n)",
    "space": "O(m·n)",
    "sections": [
        (
            "What it asks",
            """
From any cell you may step to a 4-neighbour whose value is **strictly**
greater. Return the length of the longest such path, counting cells.

Ask two things. **Strictly increasing, or non-decreasing?** Strictly — and it
is the entire reason the problem is tractable, so say why: equal neighbours
create no edge, therefore no cycle, therefore the grid is a DAG and every path
is finite. Non-decreasing would allow infinite walks between equal cells.
**Can you start anywhere?** Yes, so the answer is a max over all sources, not a
path from a fixed corner.

The brute force — DFS from each of the `m·n` cells with no memoisation — is
exponential in the worst case and hopeless on the 200 × 200 limit.
""",
        ),
        (
            "The insight",
            """
Direct the edge `u → v` whenever `v` is a strictly larger neighbour. Values
strictly increase along every edge, so no cycle can exist: this is a DAG on
`m·n` nodes and at most `4·m·n` edges, and the question is its longest path.

Kahn's algorithm gives it by **peeling**. A cell's indegree is the number of
strictly *smaller* neighbours; indegree zero means a local minimum, a place a
path can start. Remove all of them at once — that is layer 1. Every cell whose
indegree drops to zero is now a minimum of what remains, and forms layer 2.

The number of layers **is** the longest path length, because a cell can only be
peeled after every smaller neighbour that feeds it, so its layer index equals
the longest increasing path ending there.

Every cell enters the queue exactly once and each of its four edges is
inspected once: O(m·n) time, O(m·n) space.
""",
        ),
        (
            "Why peel instead of recurse",
            """
The memoised DFS — `best(cell) = 1 + max(best(larger neighbours))`, cached — is
the answer most people give, and it is also O(m·n): each cell is computed once,
and memoisation *is* a lazily-discovered topological order.

The reason to write Kahn instead is **recursion depth**. A 200 × 200 snake of
strictly increasing values is a single path of 40 000 cells, so the DFS recurses
40 000 deep against Python's default limit of 1 000 and dies with
`RecursionError` on a perfectly legal input. Raising `sys.setrecursionlimit` on
a whiteboard is an admission, not a fix; the BFS peel has no stack at all.

Two details that decide a correct implementation:

- **Compute the indegree with a full pass first.** Counting it lazily during
  the peel double-counts.
- **Equal neighbours contribute nothing** in either direction. Writing `>=`
  anywhere creates two-way edges, no cell ever reaches indegree zero, the queue
  starts empty, and a flat grid returns 0 instead of 1. That is the single most
  common bug here.
""",
        ),
    ],
}

_DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def longest_increasing_path(matrix: list[list[int]]) -> int:
    if not matrix or not matrix[0]:
        return 0

    rows, cols = len(matrix), len(matrix[0])

    # indegree = how many strictly smaller neighbours feed this cell.
    indegree = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            for dr, dc in _DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] < matrix[r][c]:
                    indegree[r][c] += 1

    # Layer 1 is every local minimum. Equal neighbours create no edge at all.
    queue = deque(
        (r, c) for r in range(rows) for c in range(cols) if indegree[r][c] == 0
    )

    layers = 0
    while queue:
        layers += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in _DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] > matrix[r][c]:
                    indegree[nr][nc] -= 1
                    if indegree[nr][nc] == 0:
                        queue.append((nr, nc))

    return layers


CASES = [
    (([[9, 9, 4], [6, 6, 8], [2, 1, 1]],), 4),
    (([[3, 4, 5], [3, 2, 6], [2, 2, 1]],), 4),
    (([[1]],), 1),
    (([],), 0),
    (([[7, 7, 7], [7, 7, 7]],), 1),  # all equal — breaks any `>=` comparison
    (([[1, 2], [3, 4]],), 3),
    (([[3, 2, 1]],), 3),  # increasing right-to-left
    (([[1, 2, 3], [6, 5, 4], [7, 8, 9]],), 9),  # snake through every cell
]


def solve(matrix: list[list[int]]) -> int:
    # Pure: the peel mutates only its own indegree grid, but copy anyway so
    # CASES survive being reused across runs.
    return longest_increasing_path([row[:] for row in matrix])
