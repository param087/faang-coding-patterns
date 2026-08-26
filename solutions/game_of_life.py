"""Game of Life — LeetCode 289."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Every cell must see the original board, so write the next state into a spare bit and shift the whole board down at the end.",
    "time": "O(rows · cols)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Advance a grid of live/dead cells by one generation, **in place**. A live cell
with 2 or 3 live neighbours survives, anything else dies; a dead cell with
exactly 3 live neighbours becomes live. Neighbours are the eight surrounding
cells.

The clarifying question that matters: are the updates **simultaneous**? Yes —
every cell reads the board as it was at the start of the tick. Skipping that
and mutating as you scan is the whole failure mode of this problem.
""",
        ),
        (
            "The insight",
            """
A cell only ever needs one bit, so the second bit is free. Use bit 0 for the
current state and bit 1 for the next one:

- count neighbours with `board[ni][nj] & 1`, which always reads the *original*
  value even if that neighbour has already been visited;
- set bit 1 (`board[i][j] |= 2`) when the cell should be live next tick;
- finish with a pass of `board[i][j] >>= 1`.

The alternative is a full copy of the board, O(m·n) extra space, which is the
correct first answer to say aloud — the two-bit trick is what earns the O(1).
""",
        ),
        (
            "Follow-ups",
            """
Both of the stated follow-ups are the real interview.

- **Infinite board.** Stop storing a grid. Keep a `set` of live coordinates,
  and build a `Counter` over the neighbours of live cells only — every cell
  that can possibly be born has at least one live neighbour, so it appears in
  that counter. Cost is O(live), independent of the bounding box.
- **The board does not fit in memory.** The rule is local, so stream it: hold
  three rows at a time, emit the middle one, slide down. Only the row above,
  the current row and the row below need to be resident, which also tells you
  how to shard it across machines — by row bands with a one-row overlap.
""",
        ),
    ],
}


def game_of_life(board: list[list[int]]) -> list[list[int]]:
    if not board or not board[0]:
        return board

    rows, cols = len(board), len(board[0])

    for i in range(rows):
        for j in range(cols):
            live = 0
            for ni in range(max(i - 1, 0), min(i + 2, rows)):
                for nj in range(max(j - 1, 0), min(j + 2, cols)):
                    if (ni, nj) != (i, j):
                        live += board[ni][nj] & 1  # bit 0 is always the old state

            # bit 1 records the next state; bit 0 stays intact for the neighbours.
            if board[i][j] & 1:
                if live in (2, 3):
                    board[i][j] |= 2
            elif live == 3:
                board[i][j] |= 2

    for i in range(rows):
        for j in range(cols):
            board[i][j] >>= 1

    return board


CASES = [
    (
        ([[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]],),
        [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]],
    ),
    # Blinker: horizontal becomes vertical only if updates are simultaneous.
    (([[0, 0, 0], [1, 1, 1], [0, 0, 0]],), [[0, 1, 0], [0, 1, 0], [0, 1, 0]]),
    # Blinker pinned to the top edge — catches missing bounds checks.
    (([[1, 1, 1], [0, 0, 0], [0, 0, 0]],), [[0, 1, 0], [0, 1, 0], [0, 0, 0]]),
    (([[1, 1], [1, 1]],), [[1, 1], [1, 1]]),  # block: still life
    (([[1, 1], [1, 0]],), [[1, 1], [1, 1]]),  # the dead corner is born
    (([[1]],), [[0]]),
    (([[0]],), [[0]]),
    (([],), []),
]


def solve(board: list[list[int]]) -> list[list[int]]:
    return game_of_life([row[:] for row in board])
