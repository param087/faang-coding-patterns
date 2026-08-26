"""Set Matrix Zeroes — LeetCode 73."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Store the row and column flags inside the matrix itself — row 0 and column 0 become the marker arrays.",
    "time": "O(rows · cols)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
If a cell is 0, set its entire row and column to 0. In place.

Ask this one: **must a zero written by the algorithm trigger further
zeroing?** No — only the *original* zeroes count. Missing it gives a matrix of
all zeroes, and it is a real trap that catches people who mutate as they scan.
""",
        ),
        (
            "Give the O(m + n) solution first",
            """
Two sets — rows to blank, columns to blank — filled in one pass and applied in
a second. Correct, clear, and it earns you the right to be asked the
follow-up.

Leading with the clever version skips the part where you demonstrate you can
write the obvious one.
""",
        ),
        (
            "The O(1) version",
            """
The follow-up asks for constant extra space. The answer is to store the flags
**inside the matrix**: row 0 becomes the column flags, column 0 becomes the
row flags.

Cell `(0,0)` belongs to both, so column 0 needs one separate boolean. That
single extra variable is the whole wrinkle.
""",
        ),
        (
            "The second pass runs backwards",
            """
This is the line to point at while writing it.

The flags live in row 0 and column 0, so they must be **read before they are
themselves overwritten**. Iterating forwards zeroes a flag and then reads it as
zero, which blanks the entire matrix.

Going from the bottom-right inward means every cell consults its flags while
they are still intact.
""",
        ),
        (
            "Dry run",
            """
`[[1,1,1],[1,0,1],[1,1,1]]` — the 0 at (1,1) sets flags at (1,0) and (0,1);
the second pass blanks row 1 and column 1.

Then run `[[0,1],[1,1]]`, where the zero is **already in the flag row**. That
is the case the extra boolean exists for, and it is where a naive version
fails.
""",
        ),
    ],
}


def set_zeroes(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return matrix

    rows, cols = len(matrix), len(matrix[0])
    # (0,0) is shared by both flag arrays, so column 0 needs its own boolean.
    first_col_has_zero = any(matrix[i][0] == 0 for i in range(rows))

    for i in range(rows):
        for j in range(1, cols):
            if matrix[i][j] == 0:
                matrix[i][0] = 0  # row flag
                matrix[0][j] = 0  # column flag

    # Backwards: the flags must be read before they are overwritten.
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, 0, -1):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
        if first_col_has_zero:
            matrix[i][0] = 0

    return matrix


CASES = [
    (([[1, 1, 1], [1, 0, 1], [1, 1, 1]],), [[1, 0, 1], [0, 0, 0], [1, 0, 1]]),
    (
        ([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],),
        [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]],
    ),
    (([[0, 1], [1, 1]],), [[0, 0], [0, 1]]),  # zero already in the flag row
    (([[1, 0]],), [[0, 0]]),
    (([[1]],), [[1]]),
    (([[0]],), [[0]]),
]


def solve(matrix: list[list[int]]) -> list[list[int]]:
    return set_zeroes([row[:] for row in matrix] if matrix else matrix)
