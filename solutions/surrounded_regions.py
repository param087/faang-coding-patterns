"""Surrounded Regions — LeetCode 130."""

from __future__ import annotations

META = {
    "pattern": "graph-traversal",
    "insight": "Do not look for enclosed regions — flood the border, and everything you did not reach is enclosed by definition.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols) worst case for the stack",
    "sections": [
        (
            "What it asks",
            """
Flip every `'O'` region that is entirely surrounded by `'X'` to `'X'`. A region
touching any edge of the board survives.

Ask: in place or return a new board (in place on LeetCode, so say when you are
mutating); is diagonal contact enough to connect a region (no); can the board
be empty or a single row (yes — a 1×n board has no interior at all, so nothing
ever flips).
""",
        ),
        (
            "The insight",
            """
"Surrounded" is defined negatively, and the negation is much easier to compute:
a region survives **iff** it contains at least one border cell. So instead of
testing each region for enclosure, do one multi-source traversal seeded with
every `'O'` on the border. Mark everything it reaches as safe; sweep once more
turning marked cells back to `'O'` and every other `'O'` to `'X'`.

The three-state marker (`'O'` → `'#'` → back to `'O'`) is what keeps this to
two passes and no `visited` set. `'#'` means "reached from the border and not
yet restored"; it is also the visited flag, since a `'#'` cell no longer
matches the `== 'O'` test.
""",
        ),
        (
            "Why border-first",
            """
The natural first answer is: for each unvisited `'O'`, flood it, and if the
flood ever touches an edge, abort and leave it alone. That is *correct*, but it
is easy to get subtly wrong under pressure — you have to finish the flood (to
mark the whole region visited) even after deciding it survives, and people
return early, leaving half a region unmarked so it gets re-walked and flipped
on the next start. Doing it properly needs a second pass anyway, to flip the
regions that turned out to be enclosed.

Border-first has no such branch: nothing is ever decided per region, only per
cell. It also makes the follow-up trivial — *"count enclosed regions"* is the
same traversal with a counter, and *"Number of Enclaves"* (LeetCode 1020) is
the same traversal returning the count of unreached land.

The one detail that bites: seed **all four edges**, including the corners, and
seed them all before starting the traversal. Running four separate scans and
four separate traversals still works, but a single seeded stack is fewer lines
and cannot miss a corner.
""",
        ),
    ],
}

DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def surrounded_regions(board: list[list[str]]) -> list[list[str]]:
    if not board or not board[0]:
        return board

    rows, cols = len(board), len(board[0])
    border = {(r, c) for r in range(rows) for c in (0, cols - 1)}
    border |= {(r, c) for c in range(cols) for r in (0, rows - 1)}

    stack = [(r, c) for r, c in border if board[r][c] == "O"]
    for r, c in stack:
        board[r][c] = "#"  # '#' = reached from the border, i.e. safe

    while stack:
        r, c = stack.pop()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "O":
                board[nr][nc] = "#"
                stack.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            board[r][c] = "O" if board[r][c] == "#" else "X"

    return board


CASES = [
    (
        (
            [
                ["X", "X", "X", "X"],
                ["X", "O", "O", "X"],
                ["X", "X", "O", "X"],
                ["X", "O", "X", "X"],
            ],
        ),
        [
            ["X", "X", "X", "X"],
            ["X", "X", "X", "X"],
            ["X", "X", "X", "X"],
            ["X", "O", "X", "X"],
        ],
    ),
    # An interior 'O' rescued through a chain reaching the top edge.
    (
        ([["X", "O", "X"], ["X", "O", "X"], ["X", "X", "X"]],),
        [["X", "O", "X"], ["X", "O", "X"], ["X", "X", "X"]],
    ),
    (
        ([["X", "X", "X"], ["X", "O", "X"], ["X", "X", "X"]],),
        [["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]],
    ),
    (([["O", "O"], ["O", "O"]],), [["O", "O"], ["O", "O"]]),
    (([["O"]],), [["O"]]),
    (([["X"]],), [["X"]]),
    (([["O", "X", "O", "X", "O"]],), [["O", "X", "O", "X", "O"]]),  # 1 row: no interior
    (([],), []),
]


def solve(board: list[list[str]]) -> list[list[str]]:
    # Copy: surrounded_regions rewrites the board, and CASES are reused.
    return surrounded_regions([row[:] for row in board])
