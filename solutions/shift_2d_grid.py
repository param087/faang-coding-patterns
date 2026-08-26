"""Shift 2D Grid — LeetCode 1260."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "The grid is a flat row-major array wearing a costume; one shift is one rotation of that array, so k shifts is a single modulo.",
    "time": "O(m·n)",
    "space": "O(m·n) for the output, O(1) extra",
    "sections": [
        (
            "What it asks",
            """
One shift moves every element one position to the right; the last element of a
row wraps to the front of the next row, and the bottom-right element wraps to
the top-left. Apply `k` shifts and return the grid.

Ask two things before writing anything: **how large is k** (LeetCode caps it at
100, but the interviewer will happily say 10⁹, and that changes nothing if you
do it properly), and **may I allocate a new grid** — the in-place answer exists
but is a different, longer conversation.
""",
        ),
        (
            "The insight",
            """
Stop thinking in two dimensions. Read the grid row-major and it is just a flat
array of length `m·n`, and the wrap rules are exactly what "rotate right by
one" means on that array. Nothing about the shift is 2D except the printing.

So `k` shifts is **one** rotation by `k mod (m·n)`, and the value that lands at
`(i, j)` is the one that started `k` positions earlier:

```
flat[(i * n + j - k) mod (m * n)]
```

Simulating `k` individual shifts is the wrong first answer: at `m·n = 10⁴` and
`k = 10⁹` that is 10¹³ element moves, and even the LeetCode-sized `k = 100`
buys you nothing over doing the arithmetic once.

Be honest about what `k %= total` is doing in the code below: the trailing
`% total` already absorbs any `k`, so the reduction is defensive rather than
load bearing *here*. It becomes load bearing the moment you write the version
everyone reaches for first —

```python
rotated = flat[-k:] + flat[:-k]
```

— which quietly returns the grid **unchanged** for any `k > total` rather than
raising. (It does handle `k == 0` correctly, by the accident that `-0 == 0`;
worth knowing so you do not "fix" a bug that is not there.) Reduce first and
the whole question goes away.
""",
        ),
        (
            "The index direction, and the O(1)-space variant",
            """
Both sign errors here produce a plausible-looking grid, which is why they
survive to the interviewer's test case:

- **Rotating left instead of right.** `+ k` reads "the value here moves
  forward"; you want `- k`, "the value here came from behind". Check it on
  `[[1,2],[3,4]], k = 1` → `[[4,1],[2,3]]`. Five seconds, total certainty.
- **Negative modulo.** Python's `%` always returns a non-negative result, so
  `(0 - k) % total` is fine. In C++ or Java it is negative and you index off
  the front — write `(i * n + j - k + total) % total` there and say why.

If they ask for **O(1) extra space**: it is the three-reversal rotation applied
to the flattened index space — reverse the whole grid, reverse the first `k`
cells, reverse the remaining `total - k`, where "reverse" walks a linear index
and maps `idx → (idx // n, idx % n)`. Worth naming; only worth writing if they
push, because the flat-index version above is already O(1) *auxiliary* if you
are allowed to write into a fresh output.
""",
        ),
    ],
}


def shift_grid(grid: list[list[int]], k: int) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    m, n = len(grid), len(grid[0])
    total = m * n
    k %= total  # the whole trick: k = 10**9 now costs the same as k = 1

    flat = [value for row in grid for value in row]
    # The value landing at (i, j) started k positions earlier, hence minus k.
    return [[flat[(i * n + j - k) % total] for j in range(n)] for i in range(m)]


CASES = [
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 1), [[9, 1, 2], [3, 4, 5], [6, 7, 8]]),
    (
        ([[3, 8, 1, 9], [19, 7, 2, 5], [4, 6, 11, 10], [12, 0, 21, 13]], 4),
        [[12, 0, 21, 13], [3, 8, 1, 9], [19, 7, 2, 5], [4, 6, 11, 10]],
    ),
    # k a whole multiple of m*n — the identity, and where an un-reduced k dies.
    (([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 9), [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    # k far larger than the grid.
    (([[1, 2], [3, 4]], 101), [[4, 1], [2, 3]]),
    (([[1, 2], [3, 4]], 0), [[1, 2], [3, 4]]),
    # Single row and single column: the two shapes where a 2D index bug hides.
    (([[1, 2, 3, 4]], 2), [[3, 4, 1, 2]]),
    (([[1], [2], [3]], 1), [[3], [1], [2]]),
    # Negatives and duplicates, so equality is not doing the work for you.
    (([[-1, -1], [0, -1]], 3), [[-1, 0], [-1, -1]]),
    (([], 3), []),
]


def solve(grid: list[list[int]], k: int) -> list[list[int]]:
    return shift_grid([row[:] for row in grid], k)
