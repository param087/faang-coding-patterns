"""Matrix Diagonal Sum — LeetCode 1572."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Add both ends of row i in one pass, then subtract the centre once when n is odd because it belongs to both diagonals.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Sum the primary diagonal (`matrix[i][i]`) and the secondary diagonal
(`matrix[i][n-1-i]`) of a square matrix, counting each cell **once**.

It is a warm-up, and it is scored on whether you touch `n` cells or `n²` of
them. Scanning the whole grid and testing `i == j or i + j == n - 1` is O(n²)
for no reason — one loop over `i` reaches both diagonals directly.
""",
        ),
        (
            "The insight",
            """
```
total = sum(matrix[i][i] + matrix[i][n - 1 - i] for i in range(n))
if n % 2:
    total -= matrix[n // 2][n // 2]
```

Two cells per row, `n` rows, done. The correction exists because for odd `n`
the diagonals cross at `(n//2, n//2)` and that cell has been added twice.
""",
        ),
        (
            "Edge cases",
            """
- **Odd `n`** is the only case where the subtraction fires; a 2 × 2 or 4 × 4
  test will happily pass a version without it. Use 3 × 3, and pick a matrix
  whose centre is not 0 — the standard sample `[[1,2,3],[4,5,6],[7,8,9]]` has
  centre 5 and answer **25**, not 30.
- **`n = 1`** is the extreme version of that: both diagonals are the same single
  cell, so the answer is that value, not twice it.
- **Negative values** are allowed, so no early exit or absolute-value shortcut
  is safe.
- **Empty matrix** → 0, if the constraints permit it. Worth one clarifying
  sentence rather than one defensive branch.
""",
        ),
    ],
}


def diagonal_sum(mat: list[list[int]]) -> int:
    n = len(mat)
    total = sum(mat[i][i] + mat[i][n - 1 - i] for i in range(n))
    if n % 2:
        total -= mat[n // 2][n // 2]  # the crossing cell was counted twice
    return total


CASES = [
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), 25),  # 30 means the centre was double-counted
    (([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],), 8),  # even n: no overlap
    (([[1, 2], [3, 4]],), 10),
    (([[5]],), 5),  # one cell, counted once
    (([[2, -1, 3], [-4, 0, 5], [6, 7, -8]],), 3),  # negatives, centre 0
    (([[-1, -2], [-3, -4]],), -10),
    (([],), 0),
]


def solve(mat: list[list[int]]) -> int:
    return diagonal_sum(mat)
