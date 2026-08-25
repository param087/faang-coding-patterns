"""Rotting Oranges — LeetCode 994."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Seed the queue with every rotten orange at once — the BFS level count is the elapsed minutes.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols)",
    "sections": [
        (
            "What it asks",
            """
Each minute, a rotten orange (2) rots its four-adjacent fresh neighbours (1).
Return the minutes until none are fresh, or −1 if some can never rot.

Ask: do oranges rot diagonally (no); what if there are **no fresh oranges** at
the start (answer 0, not −1 — a real edge case); what if there are fresh ones
but no rotten ones (−1).
""",
        ),
        (
            "The insight",
            """
This is **multi-source BFS**. Seed the queue with *every* rotten orange before
the first step, and the number of levels is the number of minutes.

Running a separate BFS per rotten orange would be O(sources × cells) and —
more importantly — gives the wrong answer, because rot spreads
simultaneously rather than one source at a time.
""",
        ),
        (
            "One level equals one minute",
            """
`for _ in range(len(queue))` captures the queue's length **before** the inner
loop, which snapshots exactly the current level. Without it, the loop keeps
consuming oranges that were just added and the minute count collapses.

Same idiom as level-order traversal of a tree.
""",
        ),
        (
            "The two edge cases",
            """
Write these down before coding — they are the whole difficulty:

1. **Zero fresh oranges** → return 0 immediately, even if there are no rotten
   ones either.
2. **Any fresh orange remaining** at the end → return −1.

Tracking a `fresh` counter handles both and avoids a final grid scan.
""",
        ),
        (
            "Dry run",
            """
`[[2,1,1],[1,1,0],[0,1,1]]` → 4. Each minute the rot front advances one ring.

Then `[[2,1,1],[0,1,1],[1,0,1]]` → −1: the bottom-left orange is walled off by
zeros and can never be reached. That is the case the `fresh` counter catches.

And `[[0,2]]` → 0: no fresh oranges at all.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def oranges_rotting(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    queue: deque[tuple[int, int]] = deque()
    fresh = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c))  # every source, seeded up front
            elif grid[r][c] == 1:
                fresh += 1

    if fresh == 0:
        return 0  # nothing to rot, regardless of what is already rotten

    minutes = 0
    while queue and fresh:
        for _ in range(len(queue)):  # snapshot: exactly one minute
            r, c = queue.popleft()
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    queue.append((nr, nc))
        minutes += 1

    return minutes if fresh == 0 else -1


CASES = [
    (([[2, 1, 1], [1, 1, 0], [0, 1, 1]],), 4),
    (([[2, 1, 1], [0, 1, 1], [1, 0, 1]],), -1),
    (([[0, 2]],), 0),
    (([[0]],), 0),
    (([[1]],), -1),
    (([[2, 2], [1, 1]],), 1),
]


def solve(grid: list[list[int]]) -> int:
    return oranges_rotting([row[:] for row in grid] if grid else grid)
