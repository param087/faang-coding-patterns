"""Next Greater Element I — LeetCode 496."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Solve nums2 once with a decreasing stack into a value -> answer map; nums1 then costs one lookup per query.",
    "time": "O(n + m)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
`nums1` is a subset of `nums2`, both with **distinct** values. For each value
in `nums1`, find where it sits in `nums2` and return the first strictly greater
value to its right, or `-1`.

Two clarifications earn their keep: are the values distinct (yes — that is what
lets a hash map key on the value at all), and is *greater* strict (yes, though
with distinct values it cannot bite here).
""",
        ),
        (
            "The insight",
            """
Ignore `nums1` completely on the first pass. Sweep `nums2` with the standard
decreasing stack: when a value arrives, it is the next greater element for
**every** stacked value it exceeds, so pop them and record the answer.

```
next_greater[popped] = current
```

That is one O(n) pass producing answers for all of `nums2`. `nums1` is then a
list comprehension of dictionary lookups, defaulting to `-1`.

The naive version — for each of the `m` queries, `index()` into `nums2` and
scan right — is O(m·n). With both arrays at 1000 that is 10⁶ operations for an
Easy problem; the real cost is that it teaches you nothing transferable, and
the interviewer is asking this to see the stack.
""",
        ),
        (
            "Values, not indices — and the -1 trap",
            """
This is the one problem in the family where storing **values** on the stack is
right. Daily Temperatures wants a distance, so it needs indices; here the query
key *is* the value, so indices would only mean an extra `nums2[...]` everywhere.

The trap is the sentinel. `-1` means "nothing greater" — but LeetCode's
non-negative constraint is the only thing keeping that unambiguous. Ask whether
values can be negative; if they can, `dict.get(value, -1)` silently conflates
"no greater element" with a genuine `-1`, and you want `None` or a separate
`in` check instead.

Elements of `nums2` that never get popped keep the default: they sit on the
stack at the end, which is exactly the "no greater element" case.
""",
        ),
    ],
}


def next_greater_element(nums1: list[int], nums2: list[int]) -> list[int]:
    next_greater: dict[int, int] = {}
    stack: list[int] = []  # values, decreasing bottom -> top

    for value in nums2:
        # `value` resolves every smaller value still waiting on the stack.
        while stack and stack[-1] < value:
            next_greater[stack.pop()] = value
        stack.append(value)

    # Whatever is left on the stack has no greater element to its right.
    return [next_greater.get(value, -1) for value in nums1]


CASES = [
    (([4, 1, 2], [1, 3, 4, 2]), [-1, 3, -1]),
    (([2, 4], [1, 2, 3, 4]), [3, -1]),
    # One arrival pops a whole run: 7 5 3 1 all wait, then 2 and 4 and 6 clear them.
    (([3, 1, 5, 7], [7, 5, 3, 1, 2, 4, 6]), [4, 2, 6, -1]),
    # Strictly decreasing: nothing is ever popped.
    (([5, 4, 3], [5, 4, 3, 2, 1]), [-1, -1, -1]),
    # Negatives, where the -1 sentinel is genuinely ambiguous.
    (([-3, -1], [-1, -3, -2]), [-2, -1]),
    (([1], [1]), [-1]),
    (([], [1, 2, 3]), []),
]


def solve(nums1: list[int], nums2: list[int]) -> list[int]:
    return next_greater_element(nums1, nums2)
