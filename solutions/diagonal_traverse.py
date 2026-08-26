"""Diagonal Traverse — LeetCode 498."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Walk one cell at a time and turn at the walls; at the two corners both wall tests fire and the one you check first decides correctness.",
    "time": "O(rows · cols)",
    "space": "O(1) extra, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Read every cell of an `m × n` matrix in zig-zag diagonal order: up-right, then
down-left, alternating, starting at `(0, 0)`.

Ask whether the matrix can be rectangular (yes) and empty (yes). The direction
alternates per diagonal, not per row — cells on one diagonal share `i + j`, and
even `i + j` goes up-right.
""",
        ),
        (
            "The insight",
            """
Two ways to write it, and the choice is worth stating.

**Bucket by `i + j`.** Append each cell to `diagonals[i + j]`, then reverse the
even-indexed buckets and concatenate. Trivially correct, five lines, O(m·n)
extra space. Perfectly acceptable if you say why you picked it.

**Walk it.** Hold `(i, j)` and a direction, emit `m · n` cells, and turn when
you hit a wall. O(1) extra space, and it is the version that gets asked about,
because the turning rules are where people fall over.

Going up-right, the move is `i -= 1; j += 1` unless you are at a wall: at the
last column go **down** one and flip, otherwise at row 0 go **right** one and
flip. Down-left mirrors it: last row go right and flip, otherwise column 0 go
down and flip.
""",
        ),
        (
            "The corner where both tests fire",
            """
At `(0, cols-1)` — top-right, moving up-right — both conditions are true: you
are in the last column *and* on row 0. Check the last column **first** and move
down. Check row 0 first and you step right, off the grid.

The bottom-left corner `(rows-1, 0)` is the mirror: moving down-left, test the
last row first and move right.

Both traps need `rows > 1` and `cols > 1` to show up, so a square 3×3 sample
will not catch them reliably. Run `[[1,2,3,4],[5,6,7,8]]` and its transpose.
""",
        ),
    ],
}


def find_diagonal_order(mat: list[list[int]]) -> list[int]:
    if not mat or not mat[0]:
        return []

    rows, cols = len(mat), len(mat[0])
    result: list[int] = []
    i = j = 0
    going_up = True

    for _ in range(rows * cols):
        result.append(mat[i][j])
        if going_up:
            if j == cols - 1:  # wall test order matters at (0, cols-1)
                i += 1
                going_up = False
            elif i == 0:
                j += 1
                going_up = False
            else:
                i, j = i - 1, j + 1
        elif i == rows - 1:  # ... and at (rows-1, 0)
            j += 1
            going_up = True
        elif j == 0:
            i += 1
            going_up = True
        else:
            i, j = i + 1, j - 1

    return result


CASES = [
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 4, 7, 5, 3, 6, 8, 9]),
    (([[1, 2, 3, 4], [5, 6, 7, 8]],), [1, 2, 5, 6, 3, 4, 7, 8]),  # wide: top-right corner
    (([[1, 2], [3, 4], [5, 6], [7, 8]],), [1, 2, 3, 5, 4, 6, 7, 8]),  # tall: bottom-left corner
    (([[1, 2], [3, 4]],), [1, 2, 3, 4]),
    (([[1, 2, 3]],), [1, 2, 3]),
    (([[1], [2], [3]],), [1, 2, 3]),
    (([[7]],), [7]),
    (([],), []),
]


def solve(mat: list[list[int]]) -> list[int]:
    return find_diagonal_order(mat)
