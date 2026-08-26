"""Rotating the Box — LeetCode 1861."""

from __future__ import annotations

META = {
    "pattern": "matrix",
    "insight": "Settle the stones first in the original orientation, where gravity is a right-to-left write pointer, and only then rotate.",
    "time": "O(rows · cols)",
    "space": "O(rows · cols) for the output",
    "sections": [
        (
            "What it asks",
            """
A box grid holds stones `#`, fixed obstacles `*` and empty cells `.`. Rotate it
90° clockwise, then let gravity pull the stones down until each rests on the
floor, on an obstacle, or on another stone. Return the settled grid.

Two things to confirm: obstacles never move, and stones never pass through
them. Everything else follows from those.
""",
        ),
        (
            "The insight",
            """
Do the two steps in the **opposite order to the statement**. After a clockwise
rotation, "down" is the direction that was "right" before it — so settle first,
in the original orientation, where each row is an independent 1-D problem and
you walk it right to left.

Per row: keep `write`, the rightmost free slot. Scanning `j` from the right,

- `*` → the region to its right is sealed off, so `write = j - 1`;
- `#` → clear `row[j]`, set `row[write]`, then `write -= 1`;
- `.` → nothing.

That is one pass per row, no repeated scanning, and it handles a run of stones
stacking against an obstacle without any special case.

Then rotate. Trying it the other way — rotate, then fall down columns — works,
but you are now walking columns bottom-up while indices have been re-mapped,
which is where the bugs live.
""",
        ),
        (
            "The rotation index",
            """
Clockwise means the **first column becomes the last row**, i.e.

```
out[j][rows - 1 - i] = box[i][j]
```

or equivalently: transpose, then reverse each row. An `m × n` box returns an
`n × m` grid, so the shapes stop matching if you get it backwards — that is the
cheap check.

The other slip is the direction of gravity before rotating. Stones must fall
**right**, because right maps to down. Fall left and the sample still has the
right shape and the right number of stones, and every one of them is in the
wrong place. Test with `[["#",".","#"]]`, which must give `[["."],["#"],["#"]]`
— both stones end up in the bottom two rows and the gap floats to the top. Let
them fall left and you get the exact mirror, which still looks plausible.
""",
        ),
    ],
}


def rotate_the_box(box: list[list[str]]) -> list[list[str]]:
    if not box or not box[0]:
        return []

    rows, cols = len(box), len(box[0])

    for row in box:  # gravity, before the rotation: stones fall right
        write = cols - 1
        for j in range(cols - 1, -1, -1):
            if row[j] == "*":
                write = j - 1  # everything right of an obstacle is sealed off
            elif row[j] == "#":
                row[j] = "."
                row[write] = "#"
                write -= 1

    # Clockwise: column j, read bottom-to-top, becomes row j.
    return [[box[i][j] for i in range(rows - 1, -1, -1)] for j in range(cols)]


CASES = [
    (([["#", ".", "#"]],), [["."], ["#"], ["#"]]),
    (
        ([["#", ".", "*", "."], ["#", "#", "*", "."]],),
        [["#", "."], ["#", "#"], ["*", "*"], [".", "."]],
    ),
    (
        (
            [
                ["#", "#", "*", ".", "*", "."],
                ["#", "#", "#", "*", ".", "."],
                ["#", "#", "#", ".", "#", "."],
            ],
        ),
        [
            [".", "#", "#"],
            [".", "#", "#"],
            ["#", "#", "*"],
            ["#", "*", "."],
            ["#", ".", "*"],
            ["#", ".", "."],
        ],
    ),
    (([["#"], ["*"], ["."]],), [[".", "*", "#"]]),  # single column, shape must flip
    (([[".", "."], [".", "."]],), [[".", "."], [".", "."]]),  # nothing to fall
    (([["*", "#"]],), [["*"], ["#"]]),  # stone already resting on the floor
    (([["#", "*", "#", "."]],), [["#"], ["*"], ["."], ["#"]]),  # obstacle seals the run
]


def solve(box: list[list[str]]) -> list[list[str]]:
    return rotate_the_box([row[:] for row in box])
