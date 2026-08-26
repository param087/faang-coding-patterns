"""Spiral Matrix — LeetCode 54."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Four shrinking boundaries — and two guards that stop a single remaining row or column being read twice.",
    "time": "O(rows · cols)",
    "space": "O(1) extra, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Read every element of a matrix in spiral order: right along the top, down the
right side, left along the bottom, up the left side, then inward.

Ask: can the matrix be rectangular (yes); can it be empty (yes); is it
guaranteed non-ragged.
""",
        ),
        (
            "The insight",
            """
Four boundaries — `top`, `bottom`, `left`, `right` — that shrink as each edge
is consumed. The loop continues while `top <= bottom and left <= right`.

There is no algorithm here. It is index bookkeeping, and the question is
whether you can execute it without an off-by-one.
""",
        ),
        (
            "The two guards are the whole problem",
            """
After the rightward pass and the downward pass, a **single remaining row**
would be read again by the leftward pass — because `top` has already crossed
past it.

`if top <= bottom` prevents that. The mirrored `if left <= right` does the same
for a single remaining column.

Without them you get duplicated elements, and the duplication only appears on
matrices with an odd number of rows or columns.
""",
        ),
        (
            "Test on 1xN and Nx1",
            """
**Square matrices hide this bug completely**, and the sample input is usually
square.

Run `[[1,2,3,4]]` (one row) and `[[1],[2],[3]]` (one column) before claiming it
works. Those two cases are the entire test.
""",
        ),
        (
            "Dry run",
            """
`[[1,2,3],[4,5,6],[7,8,9]]` → `[1,2,3,6,9,8,7,4,5]`.

Trace where each boundary moves: after the top row, `top` becomes 1; after the
right column, `right` becomes 1; and so on inward until `5` is the last cell
standing.
""",
        ),
        (
            "Follow-ups",
            """
- **Spiral Matrix II** — generate an `n × n` matrix filled `1..n²` in spiral
  order. Same boundaries, writing instead of reading.
- **Spiral Matrix III** — spiral outward from an arbitrary start, walking off
  the grid and back. A direction array with growing step lengths, and a
  genuinely different shape.
""",
        ),
    ],
}


def spiral_order(matrix: list[list[int]]) -> list[int]:
    if not matrix or not matrix[0]:
        return []

    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    result: list[int] = []

    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            result.append(matrix[top][j])
        top += 1

        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1

        if top <= bottom:  # guard: don't re-read the row just consumed
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1

        if left <= right:  # guard: same, for a single remaining column
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1

    return result


CASES = [
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5]),
    (([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],), [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
    (([[1, 2, 3, 4]],), [1, 2, 3, 4]),  # single row — needs the top guard
    (([[1], [2], [3]],), [1, 2, 3]),  # single column — needs the left guard
    (([[1]],), [1]),
    (([[1, 2], [3, 4]],), [1, 2, 4, 3]),
    (([],), []),
]


def solve(matrix: list[list[int]]) -> list[int]:
    return spiral_order(matrix)
