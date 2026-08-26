"""Shortest Bridge — LeetCode 934."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "DFS to identify one island, then BFS outward from all of it at once — the ring that first touches land is the answer.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols)",
    "sections": [
        (
            "What it asks",
            """
A binary grid contains exactly two islands. Flip the fewest `0`s to `1` so the
two become connected; return that count.

Ask: exactly two islands, guaranteed (yes — no search for a third); 4-way
connectivity (yes); is the answer the number of flipped water cells, not the
number of steps between the islands. Those differ by one, and mixing them up is
the whole of the arithmetic here.
""",
        ),
        (
            "The insight",
            """
Two different traversals, back to back, and choosing the right one for each
half is the point of the problem.

1. **DFS/flood-fill to find island A.** You only need connectivity here, so
   depth-first is fine. Repaint it to `2` and *collect its cells*.
2. **BFS outward from every cell of island A at once.** Distance matters now,
   so it must be breadth-first, and it must be multi-source: the shortest
   bridge can leave from any coastal cell, and seeding a single cell measures
   the wrong distance entirely.

Expand ring by ring over water. The moment a ring's expansion sees a `1`, that
cell is island B, and the number of completed rings is the number of water
cells the bridge crosses.
""",
        ),
        (
            "The frontier is the whole island",
            """
The two mistakes that decide this problem:

- **BFS from one cell of island A.** Then you are computing "distance from
  *that* cell", which over-counts whenever the bridge should leave from
  somewhere else on the coast. On `[[1,1,1,1,1],[1,0,0,0,1],[1,0,1,0,1],
  [1,0,0,0,1],[1,1,1,1,1]]` the answer is 1, but from the wrong corner you get
  something much larger. Seed the queue with every cell of island A, including
  interior ones — they cost nothing, because their neighbours are already
  marked.
- **Off-by-one on the count.** Process the queue in whole levels
  (`for _ in range(len(queue))`) with `steps` incremented once per level.
  Return `steps` — not `steps + 1` — at the moment you *see* land, because the
  cells already dequeued at level `steps` are the water you flipped. Check
  against `[[0,1],[1,0]]`: the islands are diagonal neighbours, one flip.

Marking water as `2` when you push it is what keeps this linear; and because
island A is already `2`, the same test stops the wave from washing back over
itself.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def shortest_bridge(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    start = next(
        (r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 1
    )

    # 1. Flood island A to 2, keeping every one of its cells as a BFS source.
    island = [start]
    grid[start[0]][start[1]] = 2
    stack = [start]
    while stack:
        r, c = stack.pop()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                stack.append((nr, nc))
                island.append((nr, nc))

    # 2. Grow the whole island outwards one ring of water at a time.
    queue = deque(island)
    steps = 0
    while queue:
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue
                if grid[nr][nc] == 1:
                    return steps  # reached island B; `steps` cells were flipped
                if grid[nr][nc] == 0:
                    grid[nr][nc] = 2
                    queue.append((nr, nc))
        steps += 1

    return -1  # unreachable given the two-island guarantee


CASES = [
    (([[0, 1], [1, 0]],), 1),
    (([[0, 1, 0], [0, 0, 0], [0, 0, 1]],), 2),
    (
        (
            [
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 1, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1],
            ],
        ),
        1,
    ),
    (([[1, 0, 0, 0, 1]],), 3),
    (([[1], [0], [0], [1]],), 2),
    (([[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 1]],), 2),
]


def solve(grid: list[list[int]]) -> int:
    # Copy: shortest_bridge repaints the grid, and CASES are reused across runs.
    return shortest_bridge([row[:] for row in grid])
