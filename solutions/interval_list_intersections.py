"""Interval List Intersections — LeetCode 986."""

from __future__ import annotations

META = {
    "pattern": "intervals",
    "insight": "The intersection of two intervals is always [max of starts, min of ends] — it exists when that is not inverted.",
    "time": "O(m + n)",
    "space": "O(m + n) for the output",
    "sections": [
        (
            "What it asks",
            """
Two lists of **closed** intervals, each already sorted and internally disjoint.
Return every pairwise intersection, in order.

Ask about the two properties in the statement, because they are the licence for
two pointers: each list is sorted **and** its own intervals do not overlap. Ask
whether a single-point touch counts — `[3,5]` against `[5,7]` must yield
`[5,5]`, because these are closed intervals and that is the difference between
`<=` and `<` in the emit test.
""",
        ),
        (
            "The insight",
            """
Two things, and neither is obvious under pressure.

**First**: the intersection of `[a1,a2]` and `[b1,b2]` is always
`[max(a1,b1), min(a2,b2)]`, and it is real exactly when `max ≤ min`. One
formula, no case analysis over the four ways intervals can overlap. Writing
those four cases out is the wrong first answer — it is where the time goes and
where the off-by-one lives.

**Second**: after comparing a pair, advance the pointer whose interval **ends
first**. That interval is finished — everything remaining in the other list
starts at or after the current position and each list is internally disjoint,
so it can never intersect anything later. The one that ends later may still
catch the next interval on the other side, so it stays.

Each step retires one interval, hence O(m + n) with no sort, no heap and no
merge of the two lists.
""",
        ),
        (
            "The pointer move is the whole problem",
            """
Advancing on **start** instead of end is the classic wrong version: with
`a = [[1,10]]` and `b = [[2,3],[4,5],[6,7]]`, it retires `[1,10]` after the
first hit and returns one intersection instead of three. Compare ends.

On a tie (`a2 == b2`) either pointer may advance — both intervals genuinely
end there — so an `if/else` on `<` is enough; a three-way branch adds nothing.

Emit with `low <= high`, not `low < high`. On the LeetCode sample the pairs
`[5,10]/[1,5]` and `[24,25]/[15,24]` both produce degenerate `[x,x]`
intersections, so a strict comparison fails the given example rather than a
hidden test — run it before you claim it works.
""",
        ),
    ],
}


def interval_intersection(
    first: list[list[int]], second: list[list[int]]
) -> list[list[int]]:
    result: list[list[int]] = []
    i = j = 0

    while i < len(first) and j < len(second):
        low = max(first[i][0], second[j][0])
        high = min(first[i][1], second[j][1])
        if low <= high:  # closed intervals: a single point is an intersection
            result.append([low, high])

        # Retire whichever interval ends first; it cannot meet anything later.
        if first[i][1] < second[j][1]:
            i += 1
        else:
            j += 1

    return result


CASES = [
    (
        ([[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]),
        [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]],
    ),
    (([[1, 7]], [[3, 10]]), [[3, 7]]),
    (([[1, 10]], [[2, 3], [4, 5], [6, 7]]), [[2, 3], [4, 5], [6, 7]]),
    (([[3, 5]], [[5, 7]]), [[5, 5]]),
    (([[1, 3]], [[5, 9]]), []),
    (([], [[4, 8], [10, 12]]), []),
    (([[1, 3], [5, 9]], []), []),
]


def solve(first: list[list[int]], second: list[list[int]]) -> list[list[int]]:
    return interval_intersection(first, second)
