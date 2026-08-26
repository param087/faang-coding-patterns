"""Generate Random Point in a Circle — LeetCode 478."""

from __future__ import annotations

import math
import random

META = {
    "pattern": "randomized",
    "symbol": "Solution",
    "insight": "Draw the radius as R·sqrt(U), not R·U — area grows with r squared, so a linear radius crowds points into the centre.",
    "time": "O(1) per point",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Given a radius and a centre, return a uniformly random point **inside** the
disc — uniform over area, so every equal-sized patch is equally likely
wherever it sits.

Boundary points are allowed, which matters only for the float comparison in a
test. The real question hiding here is whether you know that *uniform in polar
coordinates is not uniform in the plane*.
""",
        ),
        (
            "The insight",
            """
Angle is easy: θ uniform on [0, 2π). Radius is not.

A ring at radius r has circumference 2πr, so the amount of area sitting near
radius r grows **linearly in r**. The fraction of the disc within radius r is

```
F(r) = πr² / πR² = (r/R)²
```

Inverse-transform sampling says: draw U uniform on [0, 1) and solve F(r) = U.
That gives

```
r = R·√U
```

The square root is doing all the work — it pushes samples outwards to
compensate for the fact that the outer rings are bigger. Then

```
x = xc + r·cos θ,   y = yc + r·sin θ
```

Two RNG calls, no loop, O(1) with no rejection.
""",
        ),
        (
            "The wrong answer, and the test that catches it",
            """
`r = R · random()` is what nearly everyone writes first. It is uniform in
*(r, θ)* space, which is a very different thing from uniform in the plane: it
puts half the points inside radius R/2, a region that is only a **quarter** of
the disc. Plotted, it is a dartboard with a dense bullseye. Nothing about a
handful of printed coordinates reveals it.

So the test is the interesting part. The `check()` below draws 40,000 points
and asserts the fraction inside R/2 is 0.25 ± 0.0125. The linear-radius
version scores 0.50 and fails by 40 standard deviations. It also checks the
mean radius, which is 2R/3 for the correct version and R/2 for the wrong one.

**The alternative worth naming:** rejection sampling. Draw x and y uniformly
in the bounding square and retry while x² + y² > R². Trivially correct, no
trigonometry, no calculus — and the acceptance rate is π/4 ≈ 78.5%, so the
expected cost is about 2.5 RNG calls versus a fixed 2. In d dimensions that
same rejection rate collapses (a 10-dimensional ball is 0.25% of its cube), so
the inverse-transform version is the one that generalises. Offer both; the
trade-off is the answer.
""",
        ),
    ],
}


class Solution:
    def __init__(self, radius: float, x_center: float, y_center: float) -> None:
        self.radius = radius
        self.x_center = x_center
        self.y_center = y_center

    def rand_point(self) -> list[float]:
        # sqrt spreads samples outwards to match the r-dr area element.
        r = self.radius * math.sqrt(random.random())
        theta = random.uniform(0, 2 * math.pi)
        return [self.x_center + r * math.cos(theta), self.y_center + r * math.sin(theta)]


CASES: list[tuple[tuple, object]] = []


def check() -> None:
    # A zero radius degenerates to the centre exactly.
    dot = Solution(0.0, -2.5, 7.0)
    assert all(dot.rand_point() == [-2.5, 7.0] for _ in range(50))

    radius, cx, cy = 3.0, -1.0, 4.0
    circle = Solution(radius, cx, cy)
    draws = 40_000
    points = [circle.rand_point() for _ in range(draws)]

    # Every point is inside, allowing for float slop at the boundary.
    distances = [math.hypot(x - cx, y - cy) for x, y in points]
    assert max(distances) <= radius + 1e-9

    # Area, not radius, must be uniform: a disc of half the radius holds a
    # QUARTER of the points. r = R * random() scores 0.5 here.
    inner = sum(1 for d in distances if d <= radius / 2)
    assert abs(inner / draws - 0.25) < 0.0125, f"inner fraction {inner / draws:.4f}"

    # And a third of the points sit inside R/sqrt(3).
    third = sum(1 for d in distances if d <= radius / math.sqrt(3))
    assert abs(third / draws - 1 / 3) < 0.014

    # Mean radius is 2R/3 for a uniform disc, R/2 for the linear-radius bug.
    assert abs(sum(distances) / draws - 2 * radius / 3) < 0.03

    # The angle must be uniform too: four quadrants, four equal shares.
    quadrants = [0, 0, 0, 0]
    for x, y in points:
        quadrants[(0 if x >= cx else 1) + (0 if y >= cy else 2)] += 1
    assert all(abs(count - draws / 4) < 600 for count in quadrants), quadrants

    # The centre offset is a pure translation — recentre and the stats hold.
    origin = Solution(1.0, 0.0, 0.0)
    shifted = [origin.rand_point() for _ in range(5_000)]
    assert all(math.hypot(x, y) <= 1.0 + 1e-9 for x, y in shifted)
    assert any(x < 0 for x, _ in shifted) and any(y < 0 for _, y in shifted)
