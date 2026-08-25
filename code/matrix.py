"""Matrix and simulation.

These problems are rarely about an algorithm — they are about executing a rule
exactly, in place, without an off-by-one. The technique worth learning is
encoding extra state inside the values you already have, so "in place" stays
genuinely O(1) extra space.
"""

from __future__ import annotations


def rotate(matrix: list[list[int]]) -> list[list[int]]:
    """Rotate an n x n matrix 90 degrees clockwise, in place.

    Transpose, then reverse each row. Two simple passes beat one clever
    four-way swap that nobody gets right at a whiteboard — and it is easy to
    verify out loud on a 2x2.
    """
    n = len(matrix)

    for i in range(n):
        for j in range(i + 1, n):  # upper triangle only, or you undo yourself
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]

    for row in matrix:
        row.reverse()

    return matrix


def spiral_order(matrix: list[list[int]]) -> list[int]:
    """Read a matrix in spiral order.

    Four moving boundaries. The two guards in the middle matter: without them
    a single remaining row gets read twice, once left-to-right and again
    right-to-left. Test on a 1xN and an Nx1 before claiming it works.
    """
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

        if top <= bottom:  # guard: don't re-read the row we just consumed
            for j in range(right, left - 1, -1):
                result.append(matrix[bottom][j])
            bottom -= 1

        if left <= right:  # guard: same, for the column
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1

    return result


def set_zeroes(matrix: list[list[int]]) -> list[list[int]]:
    """Zero out the row and column of every zero, with O(1) extra space.

    The naive fix uses two sets of markers. To drop them, store the markers
    *in the matrix itself*: row 0 and column 0 become the flag arrays. The
    only wrinkle is that cell (0,0) is shared by both, so column 0 needs one
    separate boolean.
    """
    if not matrix or not matrix[0]:
        return matrix

    rows, cols = len(matrix), len(matrix[0])
    first_col_has_zero = any(matrix[i][0] == 0 for i in range(rows))

    for i in range(rows):
        for j in range(1, cols):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0

    # Apply inwards-out, so the flags are read before they are overwritten.
    for i in range(rows - 1, -1, -1):
        for j in range(cols - 1, 0, -1):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
        if first_col_has_zero:
            matrix[i][0] = 0

    return matrix


CASES = [
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [1, 2, 3, 6, 9, 8, 7, 4, 5]),
    (([[1, 2], [3, 4]],), [1, 2, 4, 3]),
    (([[1]],), [1]),
    (([[1, 2, 3, 4]],), [1, 2, 3, 4]),
    (([[1], [2], [3]],), [1, 2, 3]),
    (([],), []),
]


def solve(matrix: list[list[int]]) -> list[int]:
    return spiral_order(matrix)


def check() -> None:
    for args, expected in CASES:
        assert spiral_order(*args) == expected

    assert rotate([[1, 2], [3, 4]]) == [[3, 1], [4, 2]]
    assert rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]

    assert set_zeroes([[1, 1, 1], [1, 0, 1], [1, 1, 1]]) == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    assert set_zeroes([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]) == [
        [0, 0, 0, 0],
        [0, 4, 5, 0],
        [0, 3, 1, 0],
    ]
