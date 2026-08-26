"""Matrix Block Sum — LeetCode 1314."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "Build the 2-D prefix sum once with a padded row and column, then every k-box is four lookups after clamping to the border.",
    "time": "O(m · n)",
    "space": "O(m · n)",
    "sections": [
        (
            "What it asks",
            """
For every cell, sum the `(2k+1) × (2k+1)` block centred on it, clipped to the
matrix border. Return the grid of those sums.

Ask what `k` can be relative to the dimensions. LeetCode allows `k` up to 100
on a 100×100 matrix, so the box routinely covers the whole grid — any solution
that assumes the box fits inside is wrong on the majority of the input.
""",
        ),
        (
            "The insight",
            """
The naive answer recomputes each block from scratch: `O(m·n·k²)`. At
`m = n = k = 100` that is 10⁸ additions, and every cell re-adds the same
values its neighbour just added.

A 2-D prefix sum `P[r][c] = sum of mat[0:r][0:c]` makes any axis-aligned
rectangle four array reads:

```
sum(r1..r2, c1..c2) = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

The corner term is added back because the two subtractions each removed the
top-left overlap — inclusion-exclusion in two dimensions.

Build `P` with **one extra row and column of zeros**. That padding is not
cosmetic: it removes every `if r == 0` branch from both the build and the
query, which is where hand-written versions go wrong under pressure.
""",
        ),
        (
            "Clamping, which is the whole difficulty",
            """
The block for cell `(i, j)` runs from `max(i - k, 0)` to `min(i + k, m - 1)`,
inclusive on both ends. Two things follow:

- **Clamp, do not skip.** `max`/`min` against the border is the entire
  handling of the edge case. There is no separate branch.
- **Inclusive → exclusive.** The prefix formula wants a half-open range, so the
  bottom-right corner is `min(i + k, m - 1) + 1`. Writing `min(i + k + 1, m)`
  is the same value and is the form less likely to be off by one.

Two checks that catch both mistakes: `k = 0` must return the input unchanged,
and `k ≥ max(m, n)` must return the grand total in every cell. If your code
passes `k = 1` on a 3×3 but fails those two, the bug is in the clamp.
""",
        ),
    ],
}


def matrix_block_sum(mat: list[list[int]], k: int) -> list[list[int]]:
    if not mat or not mat[0]:
        return []

    rows, cols = len(mat), len(mat[0])

    # Padded so P[r][c] is always readable, including r = 0 or c = 0.
    prefix = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            prefix[r + 1][c + 1] = (
                mat[r][c] + prefix[r][c + 1] + prefix[r + 1][c] - prefix[r][c]
            )

    answer = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        r1, r2 = max(i - k, 0), min(i + k + 1, rows)  # half-open after clamping
        for j in range(cols):
            c1, c2 = max(j - k, 0), min(j + k + 1, cols)
            answer[i][j] = prefix[r2][c2] - prefix[r1][c2] - prefix[r2][c1] + prefix[r1][c1]

    return answer


CASES = [
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1), [[12, 21, 16], [27, 45, 33], [24, 39, 28]]),
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2), [[45, 45, 45], [45, 45, 45], [45, 45, 45]]),
    (([[1, 2], [3, 4]], 0), [[1, 2], [3, 4]]),
    (([[-1, 2], [3, -4]], 1), [[0, 0], [0, 0]]),
    (([[1, 2, 3, 4]], 1), [[3, 6, 9, 7]]),
    (([[5]], 3), [[5]]),
    (([], 1), []),
]


def solve(mat: list[list[int]], k: int) -> list[list[int]]:
    return matrix_block_sum(mat, k)
