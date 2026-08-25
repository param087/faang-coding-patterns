"""Largest Rectangle in Histogram — LeetCode 84."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "When a bar pops another off the stack, both of that bar's boundaries arrive at the same moment.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Bars of given heights and width 1. Return the area of the largest rectangle
that fits inside the histogram.

Ask: can heights be zero (yes); must the rectangle be axis-aligned and
contiguous (yes); can the input be empty.
""",
        ),
        (
            "The framing",
            """
For each bar, the largest rectangle **using that bar as the height** extends
left until a shorter bar and right until a shorter bar. So the answer for bar
`i` is

```
heights[i] * (right[i] - left[i] - 1)
```

where `left` and `right` are the previous-smaller and next-smaller indices.
That is two runs of the monotonic-stack template, and the maximum over all
bars.
""",
        ),
        (
            "The one-pass version",
            """
The two runs fold into one. When bar `i` pops bar `j` off the stack:

- `i` **is** `j`'s next smaller element, and
- the new stack top **is** `j`'s previous smaller element.

Both boundaries arrive at the moment of the pop. That is the insight, and it
is why this is a single loop rather than three.
""",
        ),
        (
            "The detail that decides it",
            """
The width is `i - stack[-1] - 1` **after** popping — not `i - j`.

If the stack is empty after popping, the bar extends all the way to the left
edge and the width is simply `i`.

Getting this wrong gives an answer that is correct on `[2,1,5,6,2,3]` and
wrong on `[2,4]`. **Dry-run an increasing array** before claiming it works;
the sample input hides the bug.
""",
        ),
        (
            "The sentinel",
            """
Appending a `0` drains the stack at the end. Every remaining bar is then
popped by a bar shorter than all of them, so its rectangle is measured
correctly.

The alternative is a second loop after the main one — more code, more places
to be wrong.
""",
        ),
        (
            "Follow-ups",
            """
- **Maximal Rectangle** — a binary matrix. Treat each row as a histogram of
  heights accumulated from above and run this per row: O(rows × cols). That is
  the *entire* solution, and it is the point of being fluent here.
- **Largest rectangle under a line** or with a width constraint — same
  boundaries, different objective.
""",
        ),
    ],
}


def largest_rectangle_area(heights: list[int]) -> int:
    stack: list[int] = []  # indices, heights increasing bottom -> top
    best = 0

    for i, height in enumerate([*heights, 0]):  # sentinel drains the stack
        while stack and heights[stack[-1]] >= height:
            top = stack.pop()
            # After popping, the new top is `top`'s previous smaller bar.
            width = i - stack[-1] - 1 if stack else i
            best = max(best, heights[top] * width)
        stack.append(i)

    return best


CASES = [
    (([2, 1, 5, 6, 2, 3],), 10),
    (([2, 4],), 4),
    (([1, 2, 3, 4, 5],), 9),
    (([5, 4, 3, 2, 1],), 9),
    (([1],), 1),
    (([0, 0],), 0),
    (([],), 0),
]


def solve(heights: list[int]) -> int:
    return largest_rectangle_area(heights)
