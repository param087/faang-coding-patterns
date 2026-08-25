"""Container With Most Water — LeetCode 11."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Always move the shorter wall — moving the taller one is strictly dominated, so it can never be the optimum.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Given heights of vertical lines, pick two so the container they form holds the
most water. Area is `width × min(left, right)`.

Ask: can heights be zero (yes), must the two lines be distinct (yes), does the
container slope (no — the water is bounded by the shorter wall).
""",
        ),
        (
            "The real question",
            """
The code is six lines. The interviewer is asking for the **proof**, and they
will ask "how do you know you didn't skip the optimum?" almost every time.

Have the argument ready before you write the loop.
""",
        ),
        (
            "The exchange argument",
            """
Start with pointers at both ends — the widest possible container.

Area is `width × min(left, right)`. Moving *either* pointer inward shrinks the
width. So the only way to improve is for the height to increase.

If you move the **taller** wall, the height is still capped by the shorter one,
so the area cannot increase — that option is strictly dominated. Only moving
the **shorter** wall gives any chance of a taller minimum.

Therefore the shorter wall can never be part of a better container than the one
you just measured, and discarding it is safe.
""",
        ),
        (
            "Dry run",
            """
`[1, 8, 6, 2, 5, 4, 8, 3, 7]`

Start at (0, 8): width 8, height min(1, 7) = 1 → area 8. Left is shorter, so
move left.

At (1, 8): width 7, height min(8, 7) = 7 → **area 49**. Right is shorter now,
so move right. Nothing later beats it.
""",
        ),
        (
            "Follow-ups",
            """
- **Trapping Rain Water** looks similar and is a different problem — there you
  accumulate water at every index rather than picking one pair. It is solved by
  two pointers or a [monotonic stack](../../patterns/monotonic-stack/).
- **"What if the container could hold water at an angle?"** — the `min` no
  longer bounds it and the exchange argument collapses.
""",
        ),
    ],
}


def max_area(heights: list[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0

    while left < right:
        best = max(best, (right - left) * min(heights[left], heights[right]))
        # Moving the taller wall cannot help: the shorter one still caps it.
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    return best


CASES = [
    (([1, 8, 6, 2, 5, 4, 8, 3, 7],), 49),
    (([1, 1],), 1),
    (([4, 3, 2, 1, 4],), 16),
    (([1, 2, 1],), 2),
    (([1],), 0),
    (([],), 0),
]


def solve(heights: list[int]) -> int:
    return max_area(heights)
