"""Flood Fill — LeetCode 733."""

from __future__ import annotations

META = {
    "pattern": "graph-traversal",
    "insight": "One traversal, and the only real trap is repainting a region with the colour it already has.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols) worst case for the stack",
    "sections": [
        (
            "What it asks",
            """
Starting from one pixel, repaint every 4-directionally connected pixel that
shares the start pixel's original colour.

Ask: 4-way or 8-way connectivity (4-way here, but it is one line either way);
may I modify the image in place; can the new colour equal the old one — that
last question is the whole problem.
""",
        ),
        (
            "The insight",
            """
A grid is a graph whose vertices are cells and whose edges join orthogonal
neighbours. "Connected region of the same colour" is a connected component, so
this is one traversal from a known start — BFS or DFS, no difference, because
you need reachability and not distance.

The `image[nr][nc] == start` test is doing double duty: it is both the "is this
part of the region" test **and** the visited test, because once a cell is
repainted it can never match `start` again. That is why no separate `visited`
set is needed.
""",
        ),
        (
            "The infinite loop",
            """
If `newColor == image[sr][sc]`, repainting changes nothing, so the "already
visited" test never becomes true and a naive DFS revisits the same cells until
the stack dies. The guard is one line at the top:

```python
if image[sr][sc] == colour:
    return image
```

Volunteer that check before you are asked — it is the only thing this problem
is really testing, and every LeetCode-style variant of it (`[[0,0,0],[0,0,0]]`
with colour 0) exists to catch exactly this.

The other habit worth keeping: mark on **push**, not on pop. Marking at pop
time lets the same cell be queued from four neighbours, and the frontier can
grow to several times the grid.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def flood_fill(image: list[list[int]], sr: int, sc: int, colour: int) -> list[list[int]]:
    start = image[sr][sc]
    if start == colour:
        return image  # else the "already painted" test never fires

    rows, cols = len(image), len(image[0])
    stack = [(sr, sc)]
    image[sr][sc] = colour

    while stack:
        r, c = stack.pop()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and image[nr][nc] == start:
                image[nr][nc] = colour  # mark on push, not on pop
                stack.append((nr, nc))

    return image


CASES = [
    (([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2), [[2, 2, 2], [2, 2, 0], [2, 0, 1]]),
    (([[0, 0, 0], [0, 0, 0]], 0, 0, 0), [[0, 0, 0], [0, 0, 0]]),  # would never terminate
    (([[0, 0, 0], [0, 1, 0]], 1, 1, 2), [[0, 0, 0], [0, 2, 0]]),
    (([[5]], 0, 0, 3), [[3]]),
    (([[1, 0], [0, 1]], 0, 0, 2), [[2, 0], [0, 1]]),  # diagonals are not connected
    (([[1, 1], [1, 1]], 1, 1, 2), [[2, 2], [2, 2]]),
]


def solve(image: list[list[int]], sr: int, sc: int, colour: int) -> list[list[int]]:
    # Copy: flood_fill paints in place and CASES are reused across runs.
    return flood_fill([row[:] for row in image], sr, sc, colour)
