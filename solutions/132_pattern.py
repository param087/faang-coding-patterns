"""132 Pattern — LeetCode 456."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Scan right to left: whatever a bigger value pops off the stack is the best possible '2', so any smaller value to its left wins.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Decide whether indices `i < j < k` exist with `nums[i] < nums[k] < nums[j]` —
a value, then a strictly higher peak, then something strictly between the two.
Return a boolean only; no indices required.

Note the ordering of the comparisons before you start: the *middle* value comes
last in the array. Confusing 132 with 123 or 213 is the single commonest way to
lose this problem, so write the inequality on the board.

Triple loops are O(n³); at n = 2·10⁵ that is not worth a number. Even the
obvious improvement — a prefix minimum for the `1`, then a nested scan for the
`3` and the `2` — is O(n²), i.e. 4·10¹⁰ operations.
""",
        ),
        (
            "The insight",
            """
Scan **right to left** and maintain, alongside a decreasing stack, a variable
`third`: the largest value seen so far that already has a strictly larger value
to its right. That is precisely a candidate for the `2` in the pattern, with its
`3` already found.

Then the test at each new value is a single comparison:

```python
if value < third:
    return True
```

Any `value` below `third` is a valid `1`, and it sits to the left of both. Done.

`third` is maintained by the stack: when the arriving value exceeds the top, the
top has found a bigger element to its right, so pop it into `third`. Because the
stack is decreasing, the last thing popped is the largest such candidate — and
the larger `third` is, the easier the final comparison is to satisfy, so keeping
the maximum is exactly right. It is safe to overwrite `third` with a bigger
value, because the value that pops it is still to its right.
""",
        ),
        (
            "Why right to left",
            """
Left to right, you would be searching for the `2` after fixing `1` and `3`, and
there is no way to summarise "some value strictly between these two, later on"
in O(1). Right to left, both later elements are already digested into one
number and the earliest element is the one being asked about — the direction is
what collapses the problem.

Details worth guarding:

- Test `value < third` **before** doing any popping for this value. A value
  cannot serve as both the `1` and the `3` of the same triple, and checking
  after the pops lets it.
- All comparisons are strict. `[2, 2, 2]` and `[1, 3, 3]` must both be `False`;
  a `<=` anywhere makes flat runs report a pattern.
- Fewer than three elements is always `False`, and the loop handles that with no
  special case since `third` never leaves `-inf`.
""",
        ),
    ],
}

NEG_INF = float("-inf")


def find132pattern(nums: list[int]) -> bool:
    third: float = NEG_INF  # best candidate for the "2": it already has a bigger value right
    stack: list[int] = []  # values decreasing bottom -> top, candidates for the "3"

    for value in reversed(nums):
        if value < third:  # checked before popping: one element cannot be both 1 and 3
            return True
        while stack and stack[-1] < value:
            third = stack.pop()  # popped by `value`, so `value` is its "3"
        stack.append(value)

    return False


CASES = [
    (([1, 2, 3, 4],), False),
    (([3, 1, 4, 2],), True),
    (([-1, 3, 2, 0],), True),
    # 3 < 4 < 5 with the "2" three positions after the peak.
    (([3, 5, 0, 3, 4],), True),
    # Looks promising everywhere and has no pattern at all.
    (([1, 0, 1, -4, -3],), False),
    # Duplicates: strict comparisons only.
    (([2, 2, 2, 2],), False),
    (([1, 3, 2, 2],), True),
    (([-2, 1, -2],), False),
    (([1],), False),
    (([],), False),
]


def solve(nums: list[int]) -> bool:
    return find132pattern(nums)
