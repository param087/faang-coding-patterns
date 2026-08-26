"""Search a 2D Matrix — LeetCode 74."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Each row starting above the last means the grid is already one sorted array — binary search the flat index and divmod it back.",
    "time": "O(log(rows · cols))",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Decide whether a target appears in a matrix where each row is sorted and the
first value of every row is greater than the last value of the row above.

That **second** guarantee is the whole problem, and it is the thing to repeat
back before writing code. With it, reading the grid row-major gives a single
sorted sequence. Without it — rows and columns sorted independently — you are
in Search a 2D Matrix II and one binary search is simply wrong.
""",
        ),
        (
            "The insight",
            """
Binary search over `0 .. rows·cols - 1` and map each probe back with

```
value = matrix[mid // cols][mid % cols]
```

Note **`cols`**, not `rows`, in both. Dividing by the wrong dimension still
compiles, still passes a square test case, and fails on every rectangular one —
so try it on a 1 × n grid before you say you are done.

`bisect_left` over a wrapper object does the same and is fine to mention, but
the eight-line loop is faster to write than the wrapper.
""",
        ),
        (
            "Follow-ups",
            """
- **Two binary searches** — one down the first column to pick the row, one
  along that row — is the same O(log m + log n) and reads more clearly. Either
  is a good answer; the flat index is fewer edge cases.
- **Search a 2D Matrix II** (LeetCode 240) drops the row-to-row guarantee. Then
  start at the **top-right** corner: too big means move left, too small means
  move down. O(m + n), and it is a genuinely different algorithm, not a tweak.
- **Duplicates / first occurrence**: switch to a lower-bound binary search that
  keeps narrowing on equality rather than returning at the first hit.
""",
        ),
    ],
}


def search_matrix(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False

    cols = len(matrix[0])
    low, high = 0, len(matrix) * cols - 1

    while low <= high:
        mid = (low + high) // 2
        value = matrix[mid // cols][mid % cols]  # cols, not rows
        if value == target:
            return True
        if value < target:
            low = mid + 1
        else:
            high = mid - 1

    return False


MATRIX = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]

CASES = [
    ((MATRIX, 3), True),
    ((MATRIX, 13), False),  # falls between two rows
    ((MATRIX, 1), True),  # first cell
    ((MATRIX, 60), True),  # last cell
    ((MATRIX, 0), False),  # below everything
    ((MATRIX, 61), False),  # above everything
    (([[1, 3, 5, 7, 9, 11]], 9), True),  # 1 x n: wrong divisor shows up here
    (([[1], [3], [5]], 4), False),  # n x 1
    (([], 1), False),
]


def solve(matrix: list[list[int]], target: int) -> bool:
    return search_matrix(matrix, target)
