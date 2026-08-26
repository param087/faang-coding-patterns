"""Spiral Matrix II — LeetCode 59."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Same four shrinking boundaries as Spiral Matrix, writing instead of reading — and a counter that must land on exactly n².",
    "time": "O(n²)",
    "space": "O(1) extra, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Build an `n × n` matrix filled with `1 .. n²` in spiral order: right along the
top, down the right side, left along the bottom, up the left side, inward.

It is Spiral Matrix (LeetCode 54) with the data flowing the other way. If you
have written that one, say so and reuse the skeleton — the interviewer is
checking whether you recognise it, not whether you can invent it twice.
""",
        ),
        (
            "The insight",
            """
Four boundaries — `top`, `bottom`, `left`, `right` — shrinking as each edge is
filled, and a single counter that increments on every write. The loop runs
while `top <= bottom and left <= right`.

Because the grid is square you get a free assertion: when the loop exits the
counter must be exactly `n² + 1`. Any off-by-one in the four ranges shows up
immediately as a zero left somewhere in the output, so pre-fill with zeroes and
you have your own test.

The alternative shape is a direction array `[(0,1),(1,0),(0,-1),(-1,0)]`,
stepping until the next cell is off the grid or already non-zero, then turning.
It is shorter to remember and generalises to rectangles and to Spiral Matrix
III; the boundary version is easier to argue is correct.
""",
        ),
        (
            "Odd n and the centre cell",
            """
The two guards carried over from LeetCode 54 are not decoration.

When `n` is odd, the innermost ring is a **single cell**. The rightward pass
writes it and pushes `top` past `bottom`; without `if top <= bottom` the
leftward pass writes over it again with the wrong number, and without
`if left <= right` the upward pass does the same.

Even `n` never exposes this — every ring is a proper rectangle — so `n = 2` and
`n = 4` will both pass a broken solution. Check `n = 3` (centre must be 9) and
`n = 5` (centre must be 25), plus `n = 1` and `n = 0`.
""",
        ),
    ],
}


def generate_matrix(n: int) -> list[list[int]]:
    if n <= 0:
        return []

    matrix = [[0] * n for _ in range(n)]
    top, bottom, left, right = 0, n - 1, 0, n - 1
    value = 1

    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            matrix[top][j] = value
            value += 1
        top += 1

        for i in range(top, bottom + 1):
            matrix[i][right] = value
            value += 1
        right -= 1

        if top <= bottom:  # guard: the centre cell of an odd n
            for j in range(right, left - 1, -1):
                matrix[bottom][j] = value
                value += 1
            bottom -= 1

        if left <= right:  # guard: mirrored, for a single remaining column
            for i in range(bottom, top - 1, -1):
                matrix[i][left] = value
                value += 1
            left += 1

    return matrix


CASES = [
    ((3,), [[1, 2, 3], [8, 9, 4], [7, 6, 5]]),  # odd: centre is 9
    ((1,), [[1]]),
    ((2,), [[1, 2], [4, 3]]),
    ((4,), [[1, 2, 3, 4], [12, 13, 14, 5], [11, 16, 15, 6], [10, 9, 8, 7]]),
    (
        (5,),
        [
            [1, 2, 3, 4, 5],
            [16, 17, 18, 19, 6],
            [15, 24, 25, 20, 7],
            [14, 23, 22, 21, 8],
            [13, 12, 11, 10, 9],
        ],
    ),
    ((0,), []),
]


def solve(n: int) -> list[list[int]]:
    return generate_matrix(n)
