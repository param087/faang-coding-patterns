"""Image Overlap — LeetCode 835."""

from __future__ import annotations

from collections import Counter

META = {
    "pattern": "matrix",
    "insight": "Every pair of ones votes for the one shift that would align them; the shift with the most votes is the answer.",
    "time": "O(k²) where k is the number of ones, bounded by O(n⁴)",
    "space": "O(k²) for the vote counter",
    "sections": [
        (
            "What it asks",
            """
Two `n × n` binary grids. Slide one of them by any integer offset — left,
right, up, down, no rotation — and count the positions where both hold a 1.
Return the largest such count. Bits pushed off the edge are lost, not wrapped.

Ask about wrapping and rotation explicitly. If bits wrapped, the answer would
be a cyclic cross-correlation and a completely different solution.
""",
        ),
        (
            "The insight",
            """
Stop thinking about the grids and think about the **ones**. A one at `(a, b)`
in the first image lands on a one at `(c, d)` in the second under exactly one
shift: `(c - a, d - b)`. So every pair of ones is a single vote for a single
shift, and the answer is the most-voted shift:

```
Counter((a - c, b - d) for (a, b) in ones1 for (c, d) in ones2)
```

Nothing checks that the shift is in range, and nothing has to — a shift no
translation can reach simply never collects a vote. `default=0` covers the
all-zero image, which is the case that crashes a bare `max`.
""",
        ),
        (
            "The cost, honestly",
            """
Do not oversell this. With `n ≤ 30` the brute force — try all `(2n-1)² = 3481`
offsets, count `n² = 900` cells each — is about 3.1 million operations and
passes comfortably. The vote counter on a **fully dense** pair is `900 × 900`
= 810 000 pairs, so it is only ~4× better in the worst case.

Where it actually wins is sparsity: 20 ones per image is 400 pairs regardless
of `n`, so the counter scales to a 10⁴ × 10⁴ grid where enumerating offsets
does not. State that trade-off — the pairing argument is what is being marked,
and claiming an asymptotic win that is not there is worse than not claiming it.

For a dense-but-small grid the fastest practical version is bitmasks: pack each
row into an `int`, shift with `<<` and `>>`, and count with `bin(x).count("1")`
— same O(n⁴) but with word-parallel constant factors.
""",
        ),
    ],
}


def largest_overlap(img1: list[list[int]], img2: list[list[int]]) -> int:
    ones1 = [(i, j) for i, row in enumerate(img1) for j, value in enumerate(row) if value]
    ones2 = [(i, j) for i, row in enumerate(img2) for j, value in enumerate(row) if value]

    # Each pair of ones votes for the single translation that would align them.
    shifts = Counter((a - c, b - d) for a, b in ones1 for c, d in ones2)
    return max(shifts.values(), default=0)


CASES = [
    (
        ([[1, 1, 0], [0, 1, 0], [0, 1, 0]], [[0, 0, 0], [0, 1, 1], [0, 0, 1]]),
        3,
    ),
    # A non-zero shift beats the identity, which scores 0.
    (([[1, 0], [0, 0]], [[0, 0], [0, 1]]), 1),
    (([[1, 1], [1, 1]], [[1, 1], [1, 1]]), 4),
    (([[1, 0], [0, 1]], [[0, 1], [1, 0]]), 1),  # diagonal vs anti-diagonal
    (([[0, 0], [0, 0]], [[0, 0], [0, 0]]), 0),  # no ones at all: max() would raise
    (([[1, 1], [1, 1]], [[0, 0], [0, 0]]), 0),
    (([[1]], [[1]]), 1),
    (([[1]], [[0]]), 0),
]


def solve(img1: list[list[int]], img2: list[list[int]]) -> int:
    return largest_overlap(img1, img2)
