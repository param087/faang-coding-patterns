"""Rotate Image — LeetCode 48."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "A 90-degree rotation is a transpose followed by a horizontal flip — two trivially correct passes.",
    "time": "O(n²)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Rotate an `n × n` matrix 90° clockwise, **in place**.

Ask: square or rectangular (square — rectangular rotation cannot be done in
place, since the dimensions swap); may I allocate (no); clockwise or
counter-clockwise.
""",
        ),
        (
            "The insight — decompose it",
            """
Do **not** attempt the four-way rotational swap. It is index soup at a
whiteboard and nobody gets it right under pressure.

> A 90° clockwise rotation is a **transpose** followed by a **reverse of each
> row**.

Say that and the interviewer relaxes, because it means you will not spend
eight minutes on arithmetic. Two simple passes, each easy to verify aloud.
""",
        ),
        (
            "Verify on a 2x2",
            """
Five seconds, and it removes all doubt:

`[[1,2],[3,4]]` transposes to `[[1,3],[2,4]]`; reverse each row →
`[[3,1],[4,2]]`. Correct.
""",
        ),
        (
            "The line to point at",
            """
`for j in range(i + 1, n)` — the **upper triangle only**.

Iterating the full square swaps every pair twice and leaves the matrix
unchanged. That is the bug, and it produces output identical to the input,
which is confusing to debug if you have not anticipated it.
""",
        ),
        (
            "The other three rotations",
            """
Having all of them ready costs nothing:

- **Clockwise 90°** — transpose, then reverse each row.
- **Counter-clockwise 90°** — transpose, then reverse each *column*
  (equivalently: reverse the rows first, then transpose).
- **180°** — reverse the rows and reverse each row.
""",
        ),
    ],
}


def rotate(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)

    # Transpose. Upper triangle only, or every pair swaps twice.
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

    # Reverse each row.
    for row in matrix:
        row.reverse()

    return matrix


CASES = [
    (([[1, 2], [3, 4]],), [[3, 1], [4, 2]]),
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
    (([[1]],), [[1]]),
    (
        ([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],),
        [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]],
    ),
    (([],), []),
]


def solve(matrix: list[list[int]]) -> list[list[int]]:
    return rotate([row[:] for row in matrix] if matrix else matrix)
