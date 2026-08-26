"""Toeplitz Matrix — LeetCode 766."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "One comparison per cell against its up-left neighbour; the interview is entirely about the memory-constrained follow-up.",
    "time": "O(rows · cols)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return whether every top-left-to-bottom-right diagonal of the matrix holds a
single repeated value.

The one-liner is `matrix[i][j] == matrix[i-1][j-1]` for every cell with
`i, j ≥ 1` — a cell equalling its up-left neighbour chains the whole diagonal
together, so there is nothing to collect and nothing to hash. If you catch
yourself building a dict keyed by `i - j`, you have written a correct but
heavier version of the same check.
""",
        ),
        (
            "The insight",
            """
Diagonals are indexed by `i - j`, but you never need to name them. Equality
with the up-left neighbour is **transitive along the diagonal**, so checking
each adjacent pair once covers it.

Two consequences worth saying:

- the first row and first column are never the left side of a comparison, so
  they are checked exactly once each, as the up-left neighbour of the cell
  below-right of them;
- a matrix with one row or one column is vacuously Toeplitz, and `all()` over
  an empty generator returns `True` for free.
""",
        ),
        (
            "Follow-ups",
            """
This problem is asked for its follow-ups, which are about I/O, not algorithms.

- **"One row at a time in memory."** Keep only the previous row. An incoming
  row is consistent when `row[1:] == previous[:-1]`, so two rows are ever
  resident regardless of how many there are. That comparison is the same test,
  vectorised per row.
- **"One partial row at a time."** Stream in column blocks of width `b` with a
  **one-column overlap** between consecutive blocks, so each block still has
  the up-left neighbour it needs at its left edge. Without the overlap you miss
  exactly the diagonals that cross a block boundary — the classic off-by-one
  answer to this follow-up.
""",
        ),
    ],
}


def is_toeplitz_matrix(matrix: list[list[int]]) -> bool:
    if not matrix or not matrix[0]:
        return True

    return all(
        matrix[i][j] == matrix[i - 1][j - 1]
        for i in range(1, len(matrix))
        for j in range(1, len(matrix[0]))
    )


def is_toeplitz_streamed(rows: list[list[int]]) -> bool:
    """Follow-up: only two rows resident at any moment."""
    previous: list[int] | None = None
    for row in rows:
        if previous is not None and row[1:] != previous[:-1]:
            return False
        previous = row
    return True


CASES = [
    (([[1, 2, 3, 4], [5, 1, 2, 3], [9, 5, 1, 2]],), True),
    (([[1, 2], [2, 2]],), False),
    (([[1, 2, 3], [4, 1, 2], [5, 4, 9]],), False),  # the break is in the last cell
    (([[1, 2], [3, 1], [4, 3]],), True),  # taller than wide
    (([[1, 2, 3]],), True),  # single row is vacuously true
    (([[1], [2], [3]],), True),  # single column too
    (([[7]],), True),
    (([],), True),
]


def solve(matrix: list[list[int]]) -> bool:
    result = is_toeplitz_matrix(matrix)
    assert result == is_toeplitz_streamed(matrix), "streamed variant disagrees"
    return result
