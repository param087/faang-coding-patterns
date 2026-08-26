"""Kth Smallest Element in a Sorted Matrix — LeetCode 378."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "Binary search the value, not a position: for a guess v, counting entries ≤ v takes one O(n) staircase walk from the bottom-left corner.",
    "time": "O(n log(max − min)) — an O(n) count per probe",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
An `n × n` matrix whose rows and columns are each sorted ascending. Return the
`k`-th smallest entry **in sorted order of the whole matrix**, counting
duplicates as separate entries.

Two clarifications decide the approach: duplicates are allowed and each copy
counts (so `[[1,2],[1,3]]` with `k = 2` is `1`, not `2`), and the matrix is
sorted row-wise and column-wise but **not** globally — `matrix[0][n-1]` can be
larger than `matrix[n-1][0]`, which is why you cannot index into it directly.
""",
        ),
        (
            "The insight",
            """
The obvious answers both work and both are worth naming before discarding:
flatten and sort is O(n² log n), and a min-heap merge of the rows is
O(k log n) — fine when `k` is small, but `k` can be `n²`, and at n = 300 that
is 90,000 pops.

The move that makes this a binary-search problem is to **stop searching for a
position and search for a value**. The answer lies in `[matrix[0][0],
matrix[n-1][n-1]]`, and for any candidate `v` the predicate

> "are there at least `k` entries ≤ `v`?"

is monotone in `v`. Binary search on the integer range and return the smallest
`v` that satisfies it.

Counting is the other half. Do **not** scan all n² cells — walk the staircase
from the **bottom-left** corner:

```
col fixed, values increase downward  →  matrix[row][col] is the largest in its column so far
if matrix[row][col] <= v:  the entire column above it is <= v too  →  count += row + 1; col += 1
else:                      row -= 1
```

Each step either moves right or up, so the walk is O(rows + cols) = O(n) and
never revisits a cell.

The overall cost is O(n log(max − min)). The `log` is over the *value* range,
not the input size — that is unusual enough that it is worth saying out loud,
along with the fact that it makes the search independent of `k`.
""",
        ),
        (
            "Why `low` lands on a real matrix entry",
            """
The probe values are arbitrary integers — `mid` is a midpoint of a numeric
range and may well be a number that appears nowhere in the matrix. So why is it
safe to return `low` rather than hunting for the nearest actual entry?

Because the loop converges to the **smallest** `v` with `count(v) >= k`. Suppose
that `v` were not in the matrix. Then no entry equals `v`, so
`count(v) == count(v - 1) >= k`, and `v - 1` would also satisfy the predicate —
contradicting minimality. Hence `v` is present. That argument is the one an
interviewer probes for, and it is what separates this from a formula you
half-remember.

Two implementation notes that follow from it:

- Count entries `<= mid`, never `< mid`. With duplicates, a strict comparison
  makes the predicate non-monotone against `k` and returns a value that is one
  duplicate too far right.
- The loop must be `while low < high` with `high = mid` on success and
  `low = mid + 1` on failure, and it returns `low` — never `mid`. Returning
  `mid` from inside the loop is the standard wrong answer here: `count(mid)`
  hitting `k` exactly does not make `mid` an element of the matrix.
""",
        ),
    ],
}


def kth_smallest(matrix: list[list[int]], k: int) -> int:
    rows, cols = len(matrix), len(matrix[0])

    def count_at_most(value: int) -> int:
        """Entries <= value, via one staircase walk from the bottom-left corner."""
        count = 0
        row, col = rows - 1, 0
        while row >= 0 and col < cols:
            if matrix[row][col] <= value:
                count += row + 1  # this whole column, down to row, is <= value
                col += 1
            else:
                row -= 1
        return count

    low, high = matrix[0][0], matrix[rows - 1][cols - 1]

    while low < high:
        mid = low + (high - low) // 2  # a value, not an index
        if count_at_most(mid) < k:
            low = mid + 1
        else:
            high = mid  # mid may itself be the answer

    return low  # provably a real entry — see the notes


CASES = [
    (([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8), 13),
    (([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 1), 1),
    (([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 9), 15),
    (([[1, 2], [1, 3]], 2), 1),  # duplicates: each copy counts
    (([[1, 2], [1, 3]], 3), 2),
    (([[1, 3, 5], [6, 7, 12], [11, 14, 14]], 6), 11),  # not globally sorted
    (([[-5, -4], [-5, -3]], 3), -4),  # negatives
    (([[-5]], 1), -5),
]


def solve(matrix: list[list[int]], k: int) -> int:
    return kth_smallest([row[:] for row in matrix], k)
