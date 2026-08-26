"""The Maze II — LeetCode 505."""

from __future__ import annotations

import heapq

META = {
    "pattern": "shortest-paths",
    "insight": "A roll is one edge whose weight is however far the ball travels, so the graph is weighted and BFS by roll count answers the wrong question.",
    "time": "O(R · C · max(R, C) · log(R · C))",
    "space": "O(R · C)",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so — described in my own words rather than quoted:

A grid of empty cells and walls holds a ball. You may push it in one of the
four directions, and it **keeps rolling until a wall or the border stops it**;
it cannot be halted mid-roll. Given a start and a destination cell, return the
fewest empty cells the ball travels over before **coming to rest exactly on**
the destination, or −1 if it cannot stop there.

Two clarifications decide the whole problem. Does the ball have to *stop* at
the destination, or merely pass over it? (Stop — rolling through does not
count, and that is most of the difficulty.) And is the cost the number of
pushes or the number of cells travelled? (Cells travelled — which is what makes
this weighted.)
""",
        ),
        (
            "The insight",
            """
Model each **resting position** as a node and each **push** as an edge whose
weight is the length of that roll. Weights are non-negative and vary from 1 to
`max(R, C) − 1`, so this is Dijkstra, not BFS.

That is the whole decision. Maze I — "can the ball reach the destination at
all?" — is plain BFS or DFS, because there every edge is worth the same. The
moment the question becomes *how far did it travel*, the edges stop being
uniform and roll-count BFS starts optimising the wrong quantity.

Reusing the Maze I solution is the trap. Consider

```
0 0 1 0 0
0 0 0 0 1
0 1 1 0 0
0 0 0 0 0
0 0 1 1 0
```

from `(0,0)` to `(4,4)`. There is a route that gets there in the fewest pushes
but travels 10 cells; the cheapest route takes an extra push and travels **8**.
BFS by roll count returns 10.

Inner loop: from a popped position, extend in each direction until blocked, and
relax the landing square with `distance + steps`. A zero-length roll (already
against a wall) fails the `<` test on its own, so it needs no special case.
""",
        ),
        (
            "Edge cases",
            """
- **Start equals destination** → 0. Popping the target immediately covers it;
  do not add a separate branch.
- **The destination is on a corridor the ball only passes through.** In a single
  row `[0,0,0,0]`, going from `(0,0)` to `(0,1)` is **−1** — the ball rolls
  straight to `(0,3)`. Every solution that treats "visited any cell along the
  way" as arrival gets this wrong. Only the landing squares are nodes.
- **A landing square can be improved after it is first reached**, so keep the
  stale-entry guard `if d > best[r][c]: continue` and relax on `<`, not on a
  visited set. Marking positions visited on first sight turns this into the BFS
  that returns 10 above.
- **1 × 1 grid**, or a destination fully walled off → 0 and −1 respectively,
  both handled by the same two lines.
""",
        ),
    ],
}

DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def shortest_distance(maze: list[list[int]], start: list[int], destination: list[int]) -> int:
    rows, cols = len(maze), len(maze[0])
    target = (destination[0], destination[1])

    best = [[float("inf")] * cols for _ in range(rows)]
    best[start[0]][start[1]] = 0
    heap: list[tuple[int, int, int]] = [(0, start[0], start[1])]

    while heap:
        distance, r, c = heapq.heappop(heap)
        if (r, c) == target:
            return distance
        if distance > best[r][c]:  # stale entry, a better push already landed here
            continue
        for dr, dc in DIRECTIONS:
            nr, nc, steps = r, c, 0
            while 0 <= nr + dr < rows and 0 <= nc + dc < cols and maze[nr + dr][nc + dc] == 0:
                nr += dr
                nc += dc
                steps += 1  # the ball cannot stop early; this whole roll is one edge
            if distance + steps < best[nr][nc]:
                best[nr][nc] = distance + steps
                heapq.heappush(heap, (distance + steps, nr, nc))

    return -1


CASES = [
    (([[0, 0, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 1, 0], [1, 1, 0, 1, 1], [0, 0, 0, 0, 0]],
      [0, 4], [4, 4]), 12),
    # The ball can never come to rest on (3,2).
    (([[0, 0, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 1, 0], [1, 1, 0, 1, 1], [0, 0, 0, 0, 0]],
      [0, 4], [3, 2]), -1),
    # Fewest pushes travels 10; the cheapest route travels 8.
    (([[0, 0, 1, 0, 0], [0, 0, 0, 0, 1], [0, 1, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 1, 1, 0]],
      [0, 0], [4, 4]), 8),
    (([[0]], [0, 0], [0, 0]), 0),
    (([[0, 0, 0, 0]], [0, 0], [0, 3]), 3),
    # Rolls straight past the destination.
    (([[0, 0, 0, 0]], [0, 0], [0, 1]), -1),
    (([[0, 1], [1, 0]], [0, 0], [1, 1]), -1),
]


def solve(maze: list[list[int]], start: list[int], destination: list[int]) -> int:
    return shortest_distance([row[:] for row in maze], list(start), list(destination))
