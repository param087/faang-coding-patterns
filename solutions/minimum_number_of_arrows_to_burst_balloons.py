"""Minimum Number of Arrows to Burst Balloons — LeetCode 452."""

from __future__ import annotations

META = {
    "pattern": "intervals",
    "insight": "Shoot at the smallest end you have seen; that arrow bursts every balloon still open and commits to nothing.",
    "time": "O(n log n)",
    "space": "O(n) for the sort",
    "sections": [
        (
            "What it asks",
            """
Balloons are horizontal intervals `[x_start, x_end]`. A vertical arrow at `x`
bursts every balloon with `x_start ≤ x ≤ x_end`. Return the fewest arrows that
burst all of them.

Ask: are the endpoints **inclusive**? (Yes — so `[1,2]` and `[2,3]` fall to one
arrow at `x = 2`, and that single fact decides the comparison operator.) Is the
input sorted (no). How large can the coordinates be (±2³¹, which matters — see
below).
""",
        ),
        (
            "The insight",
            """
This is [Non-overlapping Intervals](../non-overlapping-intervals/) with the
answer read off the other side: there, you count the intervals to remove; here,
you count the **groups**. Both are interval-point cover, both are greedy on the
end coordinate.

Sort by `x_end`. Fire the first arrow at the smallest end. Every balloon whose
start is at or before that x is burst for free, so skip them all; the first
balloon that starts strictly after it needs a new arrow, fired at *its* end.

Why the end and not the start, or the middle: the balloon that closes first
forces your hand — the arrow must land at or before its end — and firing at
exactly that end is the latest legal position, so it covers the maximum number
of the balloons still open. There is nothing to gain by shooting earlier. That
exchange argument is what makes the greedy provably optimal, and it is what the
interviewer wants to hear before the code.
""",
        ),
        (
            "The two traps",
            """
**The comparison.** `start > previous_end` must be strict. With `>=`, touching
balloons `[[1,2],[2,3],[3,4],[4,5]]` report 4 arrows instead of **2** — the
endpoints are inclusive, so an arrow at the shared coordinate hits both.

**Comparator overflow.** In Python this is free. In Java or C++, sorting with
`(a, b) -> a[1] - b[1]` overflows a 32-bit int when the ends sit at opposite
extremes of the range — `[[-2³¹+2, -2³¹+3], [2³¹-2, 2³¹-1]]` sorts *backwards*
and the answer comes out wrong. Use `Integer.compare(a[1], b[1])`. Mentioning
this is a cheap way to show you have thought about the constraints even when
the language protects you.

One more: `previous_end` starts at `-inf`, not `0`. Coordinates are signed.
""",
        ),
    ],
}


def find_min_arrow_shots(points: list[list[int]]) -> int:
    arrows = 0
    previous_end = float("-inf")  # signed coordinates: 0 is not a safe seed

    for start, end in sorted(points, key=lambda balloon: balloon[1]):
        if start > previous_end:  # strict: inclusive endpoints share an arrow
            arrows += 1
            previous_end = end

    return arrows


CASES = [
    (([[10, 16], [2, 8], [1, 6], [7, 12]],), 2),
    (([[1, 2], [3, 4], [5, 6], [7, 8]],), 4),
    (([[1, 2], [2, 3], [3, 4], [4, 5]],), 2),
    (([[1, 10], [2, 3], [4, 5], [6, 7]],), 3),
    (([[-2147483646, -2147483645], [2147483646, 2147483647]],), 2),
    (([[1, 2]],), 1),
    (([],), 0),
]


def solve(points: list[list[int]]) -> int:
    return find_min_arrow_shots(points)
