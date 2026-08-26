"""Walls and Gates — LeetCode 286."""

from __future__ import annotations

from collections import deque

META = {
    "pattern": "graph-traversal",
    "insight": "Push every gate into the queue before the first pop; one wave then labels each room with its nearest gate.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols) for the queue",
    "sections": [
        (
            "What it asks",
            """
This one is premium, so — in my own words, without quoting it — you are given a
grid whose cells are one of three things: a wall, a gate, or an empty room
marked with a sentinel "infinity" (`2³¹ - 1`). Fill every empty room, in place,
with the number of steps to its **nearest** gate, moving only up, down, left and
right and never through a wall. A room no gate can reach keeps the sentinel.

Ask: can there be zero gates (yes — then nothing changes); are diagonal moves
allowed (no); must it be in place (yes, the signature returns nothing, which is
a hint that the grid itself is your distance array).
""",
        ),
        (
            "The insight",
            """
Every edge costs 1, so BFS gives shortest paths — but the question is nearest
gate over *all* gates, and running one BFS per gate is O(gates · rows · cols).
On a 250×250 grid seeded with a thousand gates that is 6 × 10⁷ cell visits,
plus a `min` merge over a thousand distance grids.

Instead, enqueue **every gate at distance 0 before the first pop**. BFS from a
set of sources explores in strict order of distance from the *nearest* source,
so the first time a room is dequeued the wave that reached it came from its
closest gate. One pass, every cell visited once.

This is the same shape as Rotting Oranges and 01 Matrix: whenever a problem
says "distance to the nearest X", the answer is a queue seeded with all the Xs.
""",
        ),
        (
            "One wave, not one per gate",
            """
The sentinel is doing double duty. `rooms[nr][nc] == INF` means both "this is
an empty room" and "not yet visited", because the moment you write a distance
into it, it stops matching. Walls (`-1`) and gates (`0`) fail the test
automatically, so there is no separate `visited` set and no special-casing.

Two things people get wrong:

- **Writing the distance on pop rather than on push.** Then a room can be
  queued from four neighbours before it is first processed, the queue grows
  several times larger than the grid, and — worse — you have to guard against
  overwriting a smaller distance with a larger one.
- **Using DFS.** Depth-first exploration reaches a room by some arbitrary path,
  so you would have to re-visit rooms whenever a shorter route turns up. That
  degenerates badly on a spiral-shaped maze. BFS's level order is exactly what
  makes the first visit optimal.

Unreachable rooms need no handling at all: the wave never touches them, so they
keep the sentinel by construction.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))
INF = 2**31 - 1  # the "empty room" sentinel


def walls_and_gates(rooms: list[list[int]]) -> list[list[int]]:
    if not rooms or not rooms[0]:
        return rooms

    rows, cols = len(rooms), len(rooms[0])
    # Every gate is a source, all at distance 0, all before the first pop.
    queue = deque(
        (r, c) for r in range(rows) for c in range(cols) if rooms[r][c] == 0
    )

    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            # == INF is simultaneously "is a room" and "unvisited".
            if 0 <= nr < rows and 0 <= nc < cols and rooms[nr][nc] == INF:
                rooms[nr][nc] = rooms[r][c] + 1  # written on push
                queue.append((nr, nc))

    return rooms


CASES = [
    (
        (
            [
                [INF, -1, 0, INF],
                [INF, INF, INF, -1],
                [INF, -1, INF, -1],
                [0, -1, INF, INF],
            ],
        ),
        [
            [3, -1, 0, 1],
            [2, 2, 1, -1],
            [1, -1, 2, -1],
            [0, -1, 3, 4],
        ],
    ),
    (([[0, INF, INF, 0]],), [[0, 1, 1, 0]]),  # nearest of two gates, from both sides
    (([[0, -1, INF]],), [[0, -1, INF]]),  # walled off: sentinel survives
    (([[INF, INF], [INF, INF]],), [[INF, INF], [INF, INF]]),  # no gates at all
    (([[0, INF], [INF, INF]],), [[0, 1], [1, 2]]),
    (([[-1]],), [[-1]]),
    (([],), []),
]


def solve(rooms: list[list[int]]) -> list[list[int]]:
    # Copy: walls_and_gates fills in place, and CASES are reused across runs.
    return walls_and_gates([row[:] for row in rooms])
