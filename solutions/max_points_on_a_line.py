"""Max Points on a Line — LeetCode 149."""

from __future__ import annotations

from collections import defaultdict
from math import gcd

META = {
    "pattern": "math-geometry",
    "insight": "Anchor on one point and every other point drops into a slope bucket — but the slope must be a reduced integer pair, never a float.",
    "time": "O(n² log C) — n² pairs, each a gcd on coordinates bounded by C",
    "space": "O(n) for one point's slope buckets",
    "sections": [
        (
            "What it asks",
            """
Given points on a plane, return the largest number of them lying on one
straight line.

Two clarifying questions carry real weight here:

- **Can points repeat?** The current constraints say all points are distinct,
  but the classic version allowed duplicates and the fix is three extra lines.
  Ask, then handle it anyway — it costs nothing and it is the difference
  between "works" and "works on their hidden tests".
- **How big are the coordinates?** `|x|, |y| <= 10⁴` here. If they were 10⁹ you
  would be talking about overflow in Java and about float precision in any
  language, so the answer to this question is what licenses your slope
  representation.
""",
        ),
        (
            "The triple loop, and the number",
            """
Take every pair as a candidate line and count how many of the remaining points
sit on it: `C(300, 2) · 300 ≈ 1.3 · 10⁷`. That **passes**. So do not claim it
is too slow — it is not, at n = 300.

Reject it for the honest reason instead: it is O(n³), and if the constraint
were n = 10⁴ that is 10¹² operations against 10⁸ for the O(n²) version. Say
that out loud and move on, because the interesting part of this problem is not
the loop structure — it is how you write down a slope.
""",
        ),
        (
            "The insight",
            """
Any line with `k >= 2` points passes through at least one point you can fix in
advance. So **anchor** on each point `i` in turn and bucket every later point
`j` by the direction of `i → j`. The largest bucket plus the anchor itself is
the best line through `i`; the answer is the max over all anchors.

Scanning only `j > i` is not an optimisation you have to justify separately —
each line is counted at its lowest-indexed point, so nothing is missed.

That is O(n²) pairs total, and the whole problem collapses into a single
question: what is the key of the bucket?
""",
        ),
        (
            "Representing a slope exactly",
            """
`dy / dx` as a float is the wrong first answer, for three separate reasons:

- **Vertical lines** divide by zero.
- **`-0.0` vs `0.0`** hash to the same value in Python but are a live trap in
  other languages.
- **Precision.** `(0,0)`, `(94911151, 94911150)`, `(94911152, 94911151)` are
  *not* collinear, but both slopes round to the same double and a float
  solution confidently returns 3. That case is in `CASES` below.

Use the reduced integer pair instead. Divide `(dx, dy)` by `gcd(dx, dy)` and
then canonicalise the sign so that a direction and its opposite share a bucket:
force `dx > 0`, or `dx == 0 and dy > 0` for the vertical case. Without that
step `(1, -1)` and `(-1, 1)` land in different buckets and you undercount.

Python's `math.gcd` works on absolute values and `//` on an exact multiple is
safe for negatives, so `(-2, 2) → (-1, 1) → (1, -1)` needs no special casing.

Duplicate points are the other half: `gcd(0, 0) == 0`, so they must be filtered
out before the division and counted into `same`, which then joins **every**
bucket rather than one of them.
""",
        ),
        (
            "Dry run",
            """
`[[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]`

Anchor `(1,1)`: `(3,2)` and `(5,3)` both reduce to `(2,1)`; `(4,1) → (1,0)`,
`(2,3) → (1,2)`, `(1,4) → (0,1)`. Best bucket 2, so 3 points through `(1,1)`.

Anchor `(3,2)`: `(4,1) → (1,-1)`. `(2,3) → (-1,1)`, which **sign-flips to
`(1,-1)`**. `(1,4) → (-2,2)`, reduces to `(-1,1)`, flips to `(1,-1)`. Bucket
`(1,-1)` holds 3, plus the anchor → **4**, the line `x + y = 5`.

Drop the sign canonicalisation and that anchor reports 2. This is the case that
decides the problem.
""",
        ),
        (
            "Follow-ups",
            """
- **"Points can repeat"** — the `same` counter above. Note that with duplicates
  the answer can exceed the number of distinct positions.
- **"Do it in better than O(n²)"** — you cannot in general; deciding whether
  any three points are collinear is 3SUM-hard, so O(n²) is the accepted bound.
- **Line Reflection (LC 356)** or **Minimum Lines to Represent a Line Chart** —
  same exact-rational trick, different wrapper. Once you can key a slope
  without floats, that whole family is one function.
- **Java/C++**: `dx * dy` never overflows here, but the cross-product form of
  the brute force, `(x₂-x₁)(y₃-y₁) == (y₂-y₁)(x₃-x₁)`, reaches 8·10⁸ with
  10⁴ coordinates — fine in `int`, not fine if coordinates grow.
""",
        ),
    ],
}


def max_points(points: list[list[int]]) -> int:
    n = len(points)
    if n <= 2:
        return n

    best = 1
    for i in range(n):
        x1, y1 = points[i]
        same = 1  # the anchor, plus any exact duplicates of it
        buckets: dict[tuple[int, int], int] = defaultdict(int)
        local_best = 0

        for j in range(i + 1, n):
            x2, y2 = points[j]
            dx, dy = x2 - x1, y2 - y1

            if dx == 0 and dy == 0:  # gcd(0, 0) == 0 — must not reach the division
                same += 1
                continue

            divisor = gcd(dx, dy)
            dx //= divisor
            dy //= divisor
            if dx < 0 or (dx == 0 and dy < 0):  # a direction and its opposite are one line
                dx, dy = -dx, -dy

            buckets[(dx, dy)] += 1
            local_best = max(local_best, buckets[(dx, dy)])

        best = max(best, local_best + same)

    return best


CASES = [
    (([[1, 1], [2, 2], [3, 3]],), 3),
    (([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]],), 4),
    (([[1, 1], [1, 2], [1, 3], [2, 5]],), 3),  # vertical line
    (([[-4, -2], [-2, -1], [0, 0], [2, 1], [4, 2], [0, 5]],), 5),  # negatives, slope 1/2
    (([[0, 0], [94911151, 94911150], [94911152, 94911151]],), 2),  # float slopes say 3
    (([[1, 1], [1, 1], [2, 2]],), 3),  # duplicates
    (([[0, 0], [1, 1]],), 2),
    (([[7, 3]],), 1),
]


def solve(points: list[list[int]]) -> int:
    return max_points([point[:] for point in points])
