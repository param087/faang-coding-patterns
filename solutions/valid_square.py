"""Valid Square — LeetCode 593."""

from __future__ import annotations

from itertools import combinations

META = {
    "pattern": "math-geometry",
    "insight": "The multiset of six pairwise squared distances is order-independent: four equal sides, two equal diagonals, diagonal² = 2·side².",
    "time": "O(1) — six distances, a sort of six items",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Four points on the plane, given in **arbitrary order**. Decide whether they are
the corners of a square.

The arbitrary order is the difficulty. `p1 p2 p3 p4` is not a traversal, so you
cannot just check consecutive edges — the input might be two opposite corners
followed by the other two. Confirm that with the interviewer, because a
solution that assumes traversal order passes the sample and fails everything
else.

Also confirm: coordinates are integers (they are), and a degenerate "square" of
side 0 does not count (it does not).
""",
        ),
        (
            "The insight",
            """
Sidestep ordering entirely by using a quantity that does not depend on it: the
**multiset of all six pairwise distances**.

For a square with side `s` that multiset is four copies of `s` and two copies of
`s√2`, whatever order the corners arrive in. So sort the six squared distances
and assert:

```
d[0] == d[1] == d[2] == d[3]      four equal sides
d[4] == d[5]                      two equal diagonals
d[4] == 2 * d[0]                  Pythagoras
d[0] > 0                          not all one point
```

Squared, so no `sqrt`, no floats, no tolerance argument — with integer
coordinates every comparison is exact. That is the reason to write it this way
rather than computing angles or normalising vectors.

The `2 · side²` line is what rules out shapes the counts alone would let
through, and it is the one you should be able to justify on the spot: it *is*
the Pythagorean theorem applied to the right angle at a corner.
""",
        ),
        (
            "The cases that break the obvious checks",
            """
- **A rhombus.** `(0,0) (2,1) (4,0) (2,-1)` has four equal sides, and any
  solution that stops at "all sides equal" says yes. Its diagonals are 4 and 16
  squared, so the sorted list starts `[4, 5, 5, 5, 5, 16]` and the very first
  equality fails. This case belongs in your own test list, not just theirs.
- **A non-square rectangle.** Four right angles, two pairs of equal sides —
  caught by the same first comparison.
- **All four points identical.** Every distance is 0, so the counts trivially
  match: 0 = 0 = 0 = 0 and 0 = 0 and 0 = 2·0. Only the explicit `d[0] > 0`
  rejects it, and it is the single most commonly missed line in this problem.
- **Three coincident points plus one.** Distances `[0, 0, 0, r, r, r]` — fails
  on `d[0] > 0` and on the 4/2 split.
- **Rotation.** `(1,0) (-1,0) (0,1) (0,-1)` is a square at 45°. Anything built
  on axis-aligned reasoning (comparing x and y spans) rejects it.
""",
        ),
    ],
}


def valid_square(
    p1: list[int],
    p2: list[int],
    p3: list[int],
    p4: list[int],
) -> bool:
    points = [p1, p2, p3, p4]
    distances = sorted(
        (ax - bx) ** 2 + (ay - by) ** 2 for (ax, ay), (bx, by) in combinations(points, 2)
    )

    side, diagonal = distances[0], distances[4]
    return (
        side > 0  # rejects four coincident points
        and distances[:4] == [side] * 4
        and distances[4] == distances[5]
        and diagonal == 2 * side  # Pythagoras: rules out anything but a square
    )


CASES = [
    (([0, 0], [1, 1], [1, 0], [0, 1]), True),
    (([0, 0], [1, 1], [1, 0], [0, 12]), False),
    (([1, 0], [-1, 0], [0, 1], [0, -1]), True),  # rotated 45°
    (([0, 0], [0, 0], [0, 0], [0, 0]), False),  # degenerate
    (([0, 0], [2, 1], [4, 0], [2, -1]), False),  # rhombus: four equal sides
    (([0, 0], [0, 2], [3, 2], [3, 0]), False),  # rectangle, not square
    (([-1, -1], [-1, 1], [1, 1], [1, -1]), True),  # negatives
    (([0, 0], [0, 0], [1, 0], [1, 1]), False),  # two coincident corners
]


def solve(p1: list[int], p2: list[int], p3: list[int], p4: list[int]) -> bool:
    return valid_square(p1[:], p2[:], p3[:], p4[:])
