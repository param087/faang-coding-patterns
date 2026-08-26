"""Maximal Rectangle — LeetCode 85."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Each row is the base of a histogram whose bar heights are the ones stacked above it, so this is Largest Rectangle run once per row.",
    "time": "O(rows x cols)",
    "space": "O(cols)",
    "sections": [
        (
            "What it asks",
            """
Given a binary matrix of `"0"` and `"1"` characters, return the area of the
largest rectangle made entirely of `"1"`.

Clarify two things fast: the cells are **strings**, not ints, on LeetCode (a
silent source of `if cell:` bugs, since `"0"` is truthy), and the rectangle must
be axis-aligned and solid.

Brute force over all rectangles is O(rows² · cols²) corner pairs plus the cost
of checking each; at 200 × 200 that is 1.6 · 10⁹ corner pairs before you have
verified a single one.
""",
        ),
        (
            "The insight",
            """
Fix the **bottom** row of the rectangle. For each column, the number of
consecutive `"1"`s ending at that row is a bar height, and the best rectangle
with that bottom row is the largest rectangle in that histogram.

So sweep rows top to bottom maintaining one `heights` array:

```python
heights[c] = heights[c] + 1 if cell == "1" else 0
```

and run the O(cols) monotonic-stack histogram routine per row. Every rectangle
of 1s has some bottom row, so nothing is missed. Total O(rows · cols) — for a
200 × 200 grid, 40 000 units of work.

Being fluent in Largest Rectangle in Histogram is the entire prerequisite here;
without it this is a Hard, with it it is ten lines on top of a known routine.
""",
        ),
        (
            "The reset, and the width after popping",
            """
Two lines decide whether this works.

**`heights[c] = 0` on a zero.** Not `heights[c] - 1`, not "skip". A zero severs
the column: no rectangle with this bottom row can pass through it. Forgetting
the reset gives a plausible-looking answer that is too large on any grid with
an interior hole.

**The width inside the histogram pass is `i - stack[-1] - 1` after the pop**,
using the *new* stack top as the left boundary, not `i - popped`. That version
is right on the LeetCode sample and wrong on an increasing row such as
`[2, 4]`. Dry-run a monotone-increasing row before you claim it works.

Guard the empty matrix and the empty row up front — `matrix[0]` on `[]` throws,
and `[[]]` is a legal input with answer 0. The pass never mutates `matrix`, so
the same input can be reused.
""",
        ),
    ],
}


def _largest_rectangle_area(heights: list[int]) -> int:
    stack: list[int] = []  # indices, heights increasing bottom -> top
    best = 0

    for i, height in enumerate([*heights, 0]):  # sentinel 0 drains the stack
        while stack and heights[stack[-1]] >= height:
            top = stack.pop()
            # The new top is `top`'s previous smaller bar, so the width spans between them.
            width = i - stack[-1] - 1 if stack else i
            best = max(best, heights[top] * width)
        stack.append(i)

    return best


def maximal_rectangle(matrix: list[list[str]]) -> int:
    if not matrix or not matrix[0]:
        return 0

    heights = [0] * len(matrix[0])
    best = 0

    for row in matrix:
        for c, cell in enumerate(row):
            heights[c] = heights[c] + 1 if cell == "1" else 0  # a zero severs the column
        best = max(best, _largest_rectangle_area(heights))

    return best


CASES = [
    (
        (
            [
                ["1", "0", "1", "0", "0"],
                ["1", "0", "1", "1", "1"],
                ["1", "1", "1", "1", "1"],
                ["1", "0", "0", "1", "0"],
            ],
        ),
        6,
    ),
    # The best rectangle is neither the tallest column nor the widest row.
    (([["1", "1", "1"], ["1", "1", "0"], ["1", "0", "0"]],), 4),
    (([["1", "1", "0", "1", "1", "1"]],), 3),
    (([["1", "1"], ["1", "1"]],), 4),
    (([["0", "0"], ["0", "0"]],), 0),
    (([["1"]],), 1),
    (([["0"]],), 0),
    (([[]],), 0),
    (([],), 0),
]


def solve(matrix: list[list[str]]) -> int:
    return maximal_rectangle([list(row) for row in matrix])
