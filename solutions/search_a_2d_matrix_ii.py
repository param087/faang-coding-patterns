"""Search a 2D Matrix II — LeetCode 240."""

from __future__ import annotations

META = {
    "pattern": "divide-and-conquer",
    "insight": "Stand at the top-right corner: every comparison there discards an entire row or an entire column, never a partial one.",
    "time": "O(m + n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Decide whether a target appears in a matrix whose rows are sorted left to
right and whose columns are sorted top to bottom.

Repeat the guarantee back before writing anything, because the sister problem
(LeetCode 74) also promises each row starts above the previous row's end. That
extra promise makes the grid one flat sorted array and one binary search
works. **Here it is absent**: row 0 can be `[1, 4, 7]` and row 1 `[2, 5, 8]`,
so flattening gives `1 4 7 2 5 8`, which is not sorted. Any answer that
bisects the flat index is wrong, not merely slow.
""",
        ),
        (
            "The insight",
            """
Pick a corner where the two orderings disagree. At the **top-right** cell,
everything to its left is smaller and everything below is larger, so a single
comparison is decisive:

- `value > target` → nothing in this **column** can help; `col -= 1`.
- `value < target` → nothing in this **row** can help; `row += 1`.

Each step retires a whole line, so the walk ends after at most `m + n` steps.
Bottom-left works identically. The other two corners do not: at the top-left,
both directions increase, so a mismatch tells you nothing about which way to
go — that is the mistake to avoid on the whiteboard.

Say why the discard is *sound*: when `matrix[r][c] > target`, column `c` is
sorted downwards from row `r`, so every remaining cell in it is at least
`matrix[r][c]`, hence strictly greater than the target.
""",
        ),
        (
            "The quadrant recursion, and why it loses",
            """
The textbook divide-and-conquer answer splits the square into four quadrants,
compares the target with the centre, and recurses. The centre only ever
eliminates **one** quadrant — the top-left if the centre is too big, the
bottom-right if it is too small — so three of four survive:

```
T(n) = 3·T(n/2) + O(1)  →  O(n^log₂3) ≈ O(n^1.585)
```

For a 1000 × 1000 grid that is roughly 55,000 recursive calls against 2,000
staircase steps. The recursion is a fine thing to mention as the "obvious"
divide-and-conquer framing, then discard: the staircase *is* divide and
conquer, it just halves the problem by a whole row or column with no recursion
at all.

Binary-searching each row is `O(m log n)`, which beats the quadrant version
but still loses to `O(m + n)` for any near-square grid.
""",
        ),
    ],
}


def search_matrix(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False

    row, col = 0, len(matrix[0]) - 1  # top-right: left is smaller, below is larger

    while row < len(matrix) and col >= 0:
        value = matrix[row][col]
        if value == target:
            return True
        if value > target:
            col -= 1  # this whole column is too big
        else:
            row += 1  # this whole row is too small

    return False


CASES = [
    (([[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16], [10, 13, 14, 17]], 5), True),
    (([[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16], [10, 13, 14, 17]], 15), False),
    # Flattening row-major gives 1 4 7 2 5 8 — unsorted, so a flat bisect fails here.
    (([[1, 4, 7], [2, 5, 8]], 2), True),
    (([[-5, -2], [-4, 3]], -4), True),
    (([[1, 1], [1, 1]], 1), True),
    (([[5]], 5), True),
    (([[5]], 2), False),
    (([], 1), False),
    (([[]], 1), False),
]


def solve(matrix: list[list[int]], target: int) -> bool:
    return search_matrix(matrix, target)
