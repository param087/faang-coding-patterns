"""Transpose Matrix — LeetCode 867."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "The result is n×m, not m×n — which is exactly why the in-place swap from Rotate Image does not carry over.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols) for the output, O(1) beyond it",
    "sections": [
        (
            "What it asks",
            """
Flip the matrix over its main diagonal: `out[j][i] = matrix[i][j]`, so an
`m × n` grid comes back `n × m`.

Ask whether the matrix is square. It usually is not — the constraints allow
`m ≠ n`, and that one fact deletes the in-place answer people reach for.
""",
        ),
        (
            "The insight",
            """
Allocate the output at the **transposed shape** and copy. Column `j` of the
input becomes row `j` of the output:

```
out = [[matrix[i][j] for i in range(rows)] for j in range(cols)]
```

`list(map(list, zip(*matrix)))` is the same thing in one line and is worth
saying out loud — then write the loop. The loop shows you can index it, and
`zip` silently truncates to the shortest row if the input is ragged.
""",
        ),
        (
            "Why in place is off the table",
            """
For a **square** matrix, swapping `matrix[i][j]` with `matrix[j][i]` for every
`j > i` transposes in place. That is the first half of Rotate Image, and it is
the answer people give reflexively here.

For `m ≠ n` the object changes shape, so a list of lists cannot be rewritten in
place at all. On a flat row-major buffer it *is* possible: element `k` moves to
`(k · rows) mod (rows·cols - 1)`, and chasing those permutation cycles
transposes with only a visited bitmap. Keep that for the follow-up rather than
opening with it.
""",
        ),
    ],
}


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    if not matrix or not matrix[0]:
        return []

    rows, cols = len(matrix), len(matrix[0])
    return [[matrix[i][j] for i in range(rows)] for j in range(cols)]


CASES = [
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), [[1, 4, 7], [2, 5, 8], [3, 6, 9]]),
    (([[1, 2, 3], [4, 5, 6]],), [[1, 4], [2, 5], [3, 6]]),  # wide: shape must change
    (([[1, 2], [3, 4], [5, 6]],), [[1, 3, 5], [2, 4, 6]]),  # tall
    (([[1, 2, 3]],), [[1], [2], [3]]),
    (([[-1], [0], [7]],), [[-1, 0, 7]]),
    (([[5]],), [[5]]),
    (([],), []),
]


def solve(matrix: list[list[int]]) -> list[list[int]]:
    return transpose(matrix)
