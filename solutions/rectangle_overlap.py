"""Rectangle Overlap — LeetCode 836."""

from __future__ import annotations

META = {
    "pattern": "math-geometry",
    "insight": "A 2-D overlap is just two 1-D interval overlaps that both hold — project onto x, project onto y, and the geometry disappears.",
    "time": "O(1)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Two axis-aligned rectangles are given as `[x1, y1, x2, y2]` — bottom-left and
top-right corners. Do they overlap in a region of **positive area**?

Two clarifications decide the code, and both are stated in the problem, which
means they are there to be noticed:

- **Axis-aligned.** No rotation, so this is not a separating-axis problem.
- **Positive area.** Rectangles that merely touch along an edge or at a corner
  do **not** count, and a degenerate rectangle with zero width or height
  overlaps nothing at all — including itself.
""",
        ),
        (
            "The insight",
            """
Do not reason about rectangles. **Project onto each axis separately.**

Two axis-aligned rectangles overlap exactly when their x-projections overlap
*and* their y-projections overlap. Each projection is a 1-D interval, and two
intervals `[a1, a2]` and `[b1, b2]` overlap with positive length precisely
when `a1 < b2 and b1 < a2`.

So the answer is four comparisons:

```
rec1[0] < rec2[2] and rec2[0] < rec1[2]      # x overlaps
and rec1[1] < rec2[3] and rec2[1] < rec1[3]  # y overlaps
```

Every `<` is strict, and that is what encodes "positive area". Swap any one of
them for `<=` and rectangles sharing an edge start reporting overlap.

The alternative is to enumerate the *non*-overlapping cases — left of, right
of, above, below — and negate:

```
not (rec1[2] <= rec2[0] or rec2[2] <= rec1[0]
     or rec1[3] <= rec2[1] or rec2[3] <= rec1[1])
```

Identical by De Morgan, and the inequalities flip to `<=`. Both are fine; the
positive form is shorter and generalises to n dimensions as a single `all()`
over axes, which is the thing to say when the follow-up is boxes in 3-D.
""",
        ),
        (
            "Edge cases",
            """
- **Shared edge** — `[0,0,1,1]` and `[1,0,2,1]` touch along `x = 1`. The
  intersection is a segment, area zero, so **False**. This is the case the
  `<=` version gets wrong and the only one most graders bother to include.
- **Shared corner** — `[0,0,1,1]` and `[1,1,2,2]`. Also False, and it falls
  out of the same strictness without a special branch.
- **Degenerate rectangle** — `[0,0,0,1]` has zero width. `0 < 0` is false, so
  it overlaps nothing, which is the intended reading of "positive area". Note
  it explicitly; an interviewer who says "and what if the rectangle is a line
  segment?" is checking that you did not add a `<=` to be safe.
- **Containment** — one rectangle wholly inside the other. All four strict
  inequalities hold; no separate case needed. Worth a test, because people
  writing the "one corner is inside the other rectangle" solution get this
  **wrong** — total containment puts *no* corner of the outer rectangle inside
  the inner one. That corner-based approach is the classic wrong first answer.
- **Negative coordinates** — the problem allows `-10⁴ … 10⁴`. Nothing in the
  comparison cares about sign; a solution built on widths or `abs` might.
- **Follow-up: the overlap area itself.** `max(0, min(x2) - max(x1)) *
  max(0, min(y2) - max(y1))`. Same projection idea, and it is the core of both
  *Rectangle Area* (223) and IoU in object detection.
- **Follow-up: n rectangles, any pair overlapping?** Do not test all
  `n(n-1)/2` pairs. Sweep a line in x, keeping an interval tree of active
  y-ranges — `O(n log n)`.
""",
        ),
    ],
}


def is_rectangle_overlap(rec1: list[int], rec2: list[int]) -> bool:
    ax1, ay1, ax2, ay2 = rec1
    bx1, by1, bx2, by2 = rec2

    # Two 1-D interval overlaps. Strict <: touching edges are not an overlap.
    return ax1 < bx2 and bx1 < ax2 and ay1 < by2 and by1 < ay2


CASES = [
    (([0, 0, 2, 2], [1, 1, 3, 3]), True),
    (([0, 0, 1, 1], [1, 0, 2, 1]), False),
    (([0, 0, 1, 1], [1, 1, 2, 2]), False),
    (([0, 0, 1, 1], [2, 2, 3, 3]), False),
    (([0, 0, 10, 10], [2, 2, 3, 3]), True),
    (([0, 0, 0, 1], [0, 0, 1, 1]), False),
    (([-5, -5, -1, -1], [-3, -3, 0, 0]), True),
    (([0, 0, 2, 2], [1, 2, 3, 4]), False),
]


def solve(rec1: list[int], rec2: list[int]) -> bool:
    return is_rectangle_overlap(rec1, rec2)
