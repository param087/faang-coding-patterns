"""Queries on Number of Points Inside a Circle — LeetCode 1828."""

from __future__ import annotations

from math import isqrt

META = {
    "pattern": "segment-tree",
    "insight": "The constraints are 500 × 500, so the honest answer is the double loop with squared distances; the value is in knowing exactly which limit would force a 2-D Fenwick instead.",
    "time": "O(n·q) for the direct scan; O(q·r + C²) with a 2-D prefix grid",
    "space": "O(1) extra for the scan; O(C²) for the grid",
    "sections": [
        (
            "What it asks",
            """
Given up to 500 points and up to 500 queries `[x, y, r]`, report for each query
how many points lie **inside or on** the circle of radius `r` centred at
`(x, y)`. Points may repeat and each query is independent — nothing is consumed.

Two things to pin down, because both are free correctness wins:

- **On the boundary counts.** Use `<=`, not `<`. `(0,0)` against `[3,4,5]` is 1.
- **Compare squared distances.** `dx² + dy² <= r²` — integers throughout, no
  `sqrt`, no float comparison deciding whether a lattice point on the rim is in
  or out. Reaching for `math.hypot` here is a small but real error.
""",
        ),
        (
            "The insight",
            """
500 points × 500 queries is 250 000 distance tests. That is the answer. The
signal here is *not* producing a data structure — it is recognising that the
limits were chosen to make the direct scan correct and then spending the
remaining time on the boundary and overflow details rather than on machinery.

Say the number out loud: `n·q = 2.5 × 10⁵`, microseconds. An interviewer who
wanted a Fenwick tree would have written `n = 10⁵`.

What makes this a segment-tree-family problem is the *second* constraint, which
is easy to miss: `0 <= x, y <= 500`. The coordinate space is bounded and tiny,
which means the points can be dropped into a 501 × 501 grid and counted with a
**2-D prefix sum**. Then each query walks its `2r + 1` columns, computes the
vertical half-chord `isqrt(r² - dx²)`, and reads that column's slice in O(1):

```
for dx in -r..r:
    dy = isqrt(r*r - dx*dx)
    total += column_count(x + dx, y - dy .. y + dy)
```

O(r) per query instead of O(n) — better as soon as the points outnumber the
radius, and the exact shape a **2-D Fenwick tree** takes once points can be
inserted or deleted between queries. `isqrt` is the right call, not
`int(sqrt(...))`: it is exact on integers, where the float version is off by one
at values like `r² - dx² = 10¹⁸`.
""",
        ),
        (
            "Follow-ups — the versions that need the tree",
            """
- **"Points arrive and are removed between queries."** The static prefix grid
  dies; a 2-D Fenwick over the 501 × 501 space gives O(log² C) per insert and
  per column-slice read, with the same half-chord loop on top. This is the
  version the tag is really about.
- **"n and q are both 10⁵, coordinates up to 10⁹."** Now nothing is bounded and
  neither approach survives. Offline by radius plus a k-d tree, or an R-tree, or
  accept approximate answers — worth saying that exact 10¹⁰ pair-tests have no
  clever exact fix in general.
- **"Rectangles instead of circles."** Straight 2-D prefix sums, O(1) per query,
  no half-chord arithmetic. Circles are the only reason for the `isqrt`.
- **"Return the points, not the count."** The count structures all collapse; you
  need the scan back, or a spatial index that stores payloads.
""",
        ),
    ],
}


def count_points(points: list[list[int]], queries: list[list[int]]) -> list[int]:
    result = []
    for cx, cy, r in queries:
        radius_squared = r * r
        inside = 0
        for px, py in points:
            dx, dy = px - cx, py - cy
            if dx * dx + dy * dy <= radius_squared:  # squared, inclusive
                inside += 1
        result.append(inside)
    return result


def count_points_grid(points: list[list[int]], queries: list[list[int]]) -> list[int]:
    """The bounded-coordinate variant: 2-D prefix sums plus a half-chord walk."""
    if not points:
        return [0] * len(queries)

    size = max(max(px, py) for px, py in points) + 1
    # prefix[i][j] = number of points with px < i and py < j.
    prefix = [[0] * (size + 1) for _ in range(size + 1)]
    for px, py in points:
        prefix[px + 1][py + 1] += 1
    for i in range(1, size + 1):
        row, above = prefix[i], prefix[i - 1]
        for j in range(1, size + 1):
            row[j] += row[j - 1] + above[j] - above[j - 1]

    result = []
    for cx, cy, r in queries:
        inside = 0
        for dx in range(-r, r + 1):
            x = cx + dx
            if not 0 <= x < size:
                continue
            half = isqrt(r * r - dx * dx)  # exact on integers, unlike sqrt()
            lo = max(cy - half, 0)
            hi = min(cy + half, size - 1)
            if lo <= hi:
                inside += prefix[x + 1][hi + 1] - prefix[x + 1][lo]
                inside -= prefix[x][hi + 1] - prefix[x][lo]
        result.append(inside)
    return result


CASES = [
    (([[1, 3], [3, 3], [5, 3], [2, 2]], [[2, 3, 1], [4, 3, 1], [1, 1, 2]]), [3, 2, 2]),
    (
        (
            [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]],
            [[1, 2, 2], [2, 2, 2], [4, 3, 2], [4, 3, 3]],
        ),
        [2, 3, 2, 4],
    ),
    # Exactly on the rim counts; one unit smaller does not.
    (([[0, 0]], [[3, 4, 5], [3, 4, 4]]), [1, 0]),
    # Duplicate points are counted separately; r = 0 is a single lattice point.
    (([[1, 1], [1, 1]], [[1, 1, 0], [0, 0, 0]]), [2, 0]),
    (([], [[0, 0, 5]]), [0]),
    (([[0, 0], [500, 500]], [[250, 250, 353], [250, 250, 354]]), [0, 2]),
    (([[2, 3]], []), []),
]


def solve(points: list[list[int]], queries: list[list[int]]) -> list[int]:
    return count_points(
        [list(point) for point in points], [list(query) for query in queries]
    )


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, (args, expected)
        # The bounded-coordinate variant must agree everywhere.
        assert count_points_grid(*args) == expected, (args, expected)
