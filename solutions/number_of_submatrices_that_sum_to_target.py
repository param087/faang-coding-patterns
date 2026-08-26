"""Number of Submatrices That Sum to Target — LeetCode 1074."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "prefix-sums",
    "insight": "Fix a pair of rows, collapse that band into a single row of column sums, and the problem is Subarray Sum Equals K.",
    "time": "O(m² · n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count the non-empty submatrices whose entries sum to `target`. Two submatrices
are different if their corner coordinates differ, so **the same values in the
same shape at a different offset count twice**.

Entries can be negative. Confirm that out loud, because it kills the sliding
window before you write it.
""",
        ),
        (
            "The insight",
            """
Brute force enumerates four corners — `O(m²n²)` submatrices — and then sums
each one. Even with an O(1) 2-D prefix sum that is `O(m²n²)`, and at
`m = n = 100` that is 10⁸ range queries.

The move is to **reduce two dimensions to one**. Fix `top`, then let `bottom`
walk downwards, maintaining `col_sum[c]` = the sum of column `c` between those
two rows. Every submatrix with exactly that top and bottom edge is now a
*contiguous subarray* of `col_sum`.

So the outer two loops enumerate `O(m²)` row bands, and each band is one pass
of Subarray Sum Equals K: keep a running prefix, and for each position add the
number of earlier prefixes equal to `running - target`.

`O(m²·n)` — 10⁶ at `m = n = 100`, comfortably inside the limit. Note the
asymmetry: put the **shorter** dimension in the squared loops if the matrix is
lopsided.
""",
        ),
        (
            "The two bugs that decide it",
            """
**Reset the counter per band.** `seen` must be rebuilt for every `(top,
bottom)` pair. Hoisting it out of the inner loop is the most common way this
solution silently overcounts — prefixes from a two-row band get matched against
prefixes from a one-row band, which is not a rectangle. A single-row matrix
cannot catch it, because there is only one band — but
`[[0,1,0],[1,1,1],[0,1,0]]` with `target = 0` returns 12 instead of 4.

**Count before you insert.** Add `seen[running - target]` to the total *first*,
then record `running`. When `target == 0` the two lines commute in the wrong
direction: inserting first makes every position match itself and you count `n`
phantom empty submatrices per band. `[[0,1,0],[1,1,1],[0,1,0]]` with
`target = 0` returns 4; get the order wrong and you get 22.

The `{0: 1}` seed is what lets a subarray starting at column 0 be found at all;
drop it and `[[904]]` with `target = 904` returns 0.
""",
        ),
    ],
}


def num_submatrix_sum_target(matrix: list[list[int]], target: int) -> int:
    if not matrix or not matrix[0]:
        return 0

    rows, cols = len(matrix), len(matrix[0])
    total = 0

    for top in range(rows):
        col_sum = [0] * cols  # column sums of the band rows[top..bottom]

        for bottom in range(top, rows):
            for c in range(cols):
                col_sum[c] += matrix[bottom][c]

            # One fresh Subarray-Sum-Equals-K pass over this band.
            seen: defaultdict[int, int] = defaultdict(int)
            seen[0] = 1
            running = 0
            for value in col_sum:
                running += value
                total += seen[running - target]  # count first...
                seen[running] += 1  # ...then record, or target=0 self-matches

    return total


CASES = [
    (([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0), 4),
    (([[1, -1], [-1, 1]], 0), 5),
    (([[1, -1], [-1, 1]], -1), 2),
    (([[0, 0], [0, 0]], 0), 9),
    (([[1, 2, 3]], 3), 2),
    (([[904]], 904), 1),
    (([[904]], 0), 0),
    (([], 0), 0),
]


def solve(matrix: list[list[int]], target: int) -> int:
    return num_submatrix_sum_target(matrix, target)
