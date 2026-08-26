"""Random Point in Non-overlapping Rectangles — LeetCode 497."""

from __future__ import annotations

import random
from bisect import bisect_left
from collections import Counter

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Weight each rectangle by its lattice-point count, not its area — then it is prefix sums plus one binary search.",
    "time": "O(n) build, O(log n) per pick",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given non-overlapping axis-aligned rectangles as `[x1, y1, x2, y2]`, return a
uniformly random **integer point** inside one of them. Corners and edges count
as inside.

The word that decides the implementation is *integer*. This is not a
continuous area problem: a 1×1 rectangle `[0,0,1,1]` contains **four** lattice
points, not one unit of area. Confirm that reading out loud, because getting
it wrong costs you the whole distribution rather than a rounding error.

Also confirm the rectangles do not overlap — otherwise a point in an
intersection would be reachable two ways and the uniformity argument
collapses.
""",
        ),
        (
            "The insight",
            """
Two independent draws collapsed into one.

**Which rectangle?** Weight rectangle i by the number of lattice points it
contains, `(x2 − x1 + 1) · (y2 − y1 + 1)`. Prefix-sum those counts and binary
search a uniform draw into `[1, total]` — the technique from
[Random Pick with Weight](../random-pick-with-weight/), with area as the
weight.

**Where inside it?** Do not draw two more random numbers. The binary search
already gives you an offset within the chosen rectangle, and unravelling that
offset in row-major order is both free and exactly uniform:

```
x = x1 + offset % width
y = y1 + offset // width
```

One RNG call per pick, O(log n) work, and the composition is uniform because
the rectangle is chosen in proportion to its point count and the point is
chosen uniformly within it.
""",
        ),
        (
            "The two +1s, and the bisect that must be left",
            """
Three off-by-ones sit on top of each other here:

- **The count.** `(x2 − x1) · (y2 − y1)` is the *area*; the lattice-point count
  needs `+1` on each side. Degenerate inputs make the difference loud: the
  point rectangle `[0,0,0,0]` has area 0 and one valid point. With the area
  formula it can never be selected, and `total` may even be 0.
- **The bisect.** Draw into `[1, total]` and use `bisect_left` on the prefix
  totals. `bisect_right`, or drawing from `[0, total)`, shifts every pick by
  one and silently hands rectangle i's mass to its neighbour — output that
  still looks random and is wrong.
- **The offset.** Subtract the previous prefix *and one more*, so the offset is
  0-based before the divmod. Off by one here pushes the last point of each
  rectangle into the first row of the next.

None of the three is visible without a histogram. The `check()` below pins the
1×1-rectangle case (four points, evenly) and a 1-versus-16 point split, which
catches all three.
""",
        ),
    ],
}


class Solution:
    def __init__(self, rects: list[list[int]]) -> None:
        self.rects = [list(rect) for rect in rects]
        self.prefix: list[int] = []
        running = 0
        for x1, y1, x2, y2 in self.rects:
            running += (x2 - x1 + 1) * (y2 - y1 + 1)  # lattice points, not area
            self.prefix.append(running)
        self.total = running

    def pick(self) -> list[int]:
        target = random.randint(1, self.total)  # 1-based, to pair with bisect_left
        r = bisect_left(self.prefix, target)
        x1, y1, x2, y2 = self.rects[r]

        before = self.prefix[r - 1] if r else 0
        offset = target - before - 1  # 0-based position inside this rectangle
        width = x2 - x1 + 1
        return [x1 + (offset % width), y1 + (offset // width)]


CASES: list[tuple[tuple, object]] = []


def _lattice_points(rect: list[int]) -> set[tuple[int, int]]:
    x1, y1, x2, y2 = rect
    return {(x, y) for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)}


def check() -> None:
    # A degenerate rectangle is a single point — area 0, count 1.
    dot = Solution([[0, 0, 0, 0]])
    assert all(dot.pick() == [0, 0] for _ in range(100))

    # A vertical segment: 6 points, no width. Negatives included.
    line = Solution([[-2, -2, -2, 3]])
    seen = Counter(tuple(line.pick()) for _ in range(30_000))
    assert set(seen) == _lattice_points([-2, -2, -2, 3])
    assert all(abs(count - 5_000) < 400 for count in seen.values())

    # The unit square holds FOUR points, evenly. Using area as the weight and
    # drawing x in [x1, x2) collapses this to a single point.
    square = Solution([[1, 1, 2, 2]])
    draws = 40_000
    corners = Counter(tuple(square.pick()) for _ in range(draws))
    assert set(corners) == {(1, 1), (1, 2), (2, 1), (2, 2)}
    for corner, count in corners.items():
        assert abs(count - draws / 4) < 500, f"{corner} came up {count} times"

    # Wildly unequal rectangles: 1 point versus 16, so the small one must win
    # 1/17 of the time. A bisect_right here shifts the mass by a whole rect.
    mixed = Solution([[0, 0, 0, 0], [10, 10, 13, 13]])
    hits = Counter(tuple(mixed.pick()) for _ in range(51_000))
    assert set(hits) <= _lattice_points([0, 0, 0, 0]) | _lattice_points([10, 10, 13, 13])
    assert abs(hits[(0, 0)] - 3_000) < 300
    assert abs(hits[(13, 13)] - 3_000) < 300

    # Every point of every rectangle must be reachable, and nothing outside.
    rects = [[-3, -3, -1, -1], [0, 0, 0, 5], [4, 4, 6, 4]]
    valid: set[tuple[int, int]] = set()
    for rect in rects:
        valid |= _lattice_points(rect)
    picker = Solution(rects)
    produced = {tuple(picker.pick()) for _ in range(20_000)}
    assert produced == valid

    # The constructor copies, so a caller mutating their input cannot corrupt us.
    caller = [[0, 0, 1, 1]]
    guarded = Solution(caller)
    caller[0][2] = 99
    assert all(tuple(guarded.pick()) in _lattice_points([0, 0, 1, 1]) for _ in range(200))
