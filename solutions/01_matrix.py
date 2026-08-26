"""01 Matrix — LeetCode 542."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Run the search backwards: seed the queue with every zero at once, and each one flows outward to its nearest cells.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols)",
    "sections": [
        (
            "What it asks",
            """
For every cell of a binary matrix, return its distance to the nearest `0`,
counting orthogonal steps. Zeros have distance 0.

Ask: is at least one `0` guaranteed (yes on LeetCode — otherwise every answer
is infinite and you must agree on a sentinel); are diagonals allowed (no); may
I write into the input matrix.
""",
        ),
        (
            "The insight",
            """
Do not BFS out from each `1`. The grid is up to 10⁴ cells on LeetCode and
larger in interviews; with ~10⁴ ones each doing a full O(10⁴) search, that is
10⁸ cell visits for a problem that is genuinely linear.

Reverse it. The relation "cell A is *k* steps from zero B" is symmetric, so
instead of every `1` searching for a zero, every zero pushes outward. Seed the
queue with **all** the zeros at distance 0. Multi-source BFS expands in strict
order of distance from the nearest source, so the first time a cell is reached,
it is reached from its closest zero — one pass, every cell dequeued once.

Keep the distances in a separate grid initialised to `-1`. That `-1` is the
visited flag, which is why you never need to compare a new distance against an
old one.
""",
        ),
        (
            "The two-pass DP alternative",
            """
There is an O(rows · cols) solution with **no queue**. Distance to the nearest
zero satisfies

```
dist[r][c] = 1 + min(dist of the four neighbours)
```

and the four neighbours split into two independent halves: up/left, and
down/right. Sweep top-left → bottom-right taking `min(up, left) + 1`, then
sweep bottom-right → top-left taking `min(down, right) + 1`. Two passes,
O(1) extra space if you write into the matrix.

The trap is doing **only the first sweep**. It is right for `[[0,1,1,1]]` and
wrong for `[[1,1,1],[1,1,1],[1,1,0]]`, where every distance is determined by a
zero that lies below and to the right; the forward pass alone has never seen
it. If you offer the DP, say "two passes" in the same breath — and initialise
unknown cells to something large enough that `+1` cannot overflow into a
plausible-looking answer.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def update_matrix(mat: list[list[int]]) -> list[list[int]]:
    if not mat or not mat[0]:
        return []

    rows, cols = len(mat), len(mat[0])
    dist = [[-1] * cols for _ in range(rows)]  # -1 doubles as "unvisited"
    queue: deque[tuple[int, int]] = deque()

    for r in range(rows):
        for c in range(cols):
            if mat[r][c] == 0:
                dist[r][c] = 0
                queue.append((r, c))  # every zero is a source

    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1  # first visit is the shortest
                queue.append((nr, nc))

    return dist


CASES = [
    (([[0, 0, 0], [0, 1, 0], [0, 0, 0]],), [[0, 0, 0], [0, 1, 0], [0, 0, 0]]),
    (([[0, 0, 0], [0, 1, 0], [1, 1, 1]],), [[0, 0, 0], [0, 1, 0], [1, 2, 1]]),
    # The zero is below and to the right: a single forward DP sweep fails here.
    (([[1, 1, 1], [1, 1, 1], [1, 1, 0]],), [[4, 3, 2], [3, 2, 1], [2, 1, 0]]),
    (([[0, 1, 1, 1]],), [[0, 1, 2, 3]]),
    (([[1], [1], [0], [1]],), [[2], [1], [0], [1]]),
    (([[0]],), [[0]]),
    (([],), []),
]


def solve(mat: list[list[int]]) -> list[list[int]]:
    return update_matrix(mat)
