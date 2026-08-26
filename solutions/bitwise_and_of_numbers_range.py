"""Bitwise AND of Numbers Range — LeetCode 201."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "ANDing a whole range keeps only the common binary prefix of the endpoints; every lower bit gets zeroed by some number in between.",
    "time": "O(log right) — at most 31 shifts for 32-bit inputs",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
AND together every integer in `[left, right]` inclusive and return the result.

The range can span two billion values, so the loop you would write first is not
on the table. Worth confirming: inclusive on both ends (yes), and `left` may
equal `right` (then the answer is `left`).
""",
        ),
        (
            "The insight",
            """
Look at bit `k`. If the range is wide enough that bit `k` flips at least once
between `left` and `right`, some member of the range has a 0 there, and the AND
of the whole range has a 0 there. So the only bits that survive are the ones
that never change across the range — the **common binary prefix** of `left` and
`right`.

Concretely: shift both endpoints right until they agree, counting the shifts,
then shift the agreed value back.

```
26 = 11010     13 = 1101     6 = 110     3 = 11
30 = 11110     15 = 1111     7 = 111     3 = 11   -> 3 << 3 = 24
```

Why "never changes" is the right test and not something subtler: if the top
differing bit is at position `k`, then `left` has 0 there and `right` has 1
there, so the range crosses `2^k` — and the number `2^k` itself, which is in the
range, has zeros in every position below `k`. That single witness kills all the
low bits at once, which is why the prefix argument is exact rather than an
approximation.

Brian Kernighan gives the same answer in a different shape: `while right >
left: right &= right - 1`, repeatedly clearing the lowest set bit of `right`
until it drops to or below `left`. Same O(log) cost, fewer lines, marginally
harder to justify at a whiteboard.
""",
        ),
        (
            "Edge cases",
            """
- `left == right` — the loop never runs, you return `left`. Correct by
  construction, but say it out loud; a solution that special-cases it is a
  solution that was not reasoned through.
- `left == 0` — the answer is 0 for any `right`, because 0 is in the range. The
  shift loop handles this without a branch: 0 stays 0.
- `[1, 2^31 - 1]` — no common prefix at all, answer 0, and the loop runs 31
  times rather than 2 billion. This is the case that separates the two
  approaches.
- **The wrong first answer** is `functools.reduce(and_, range(left, right + 1))`.
  At `left = 1, right = 2^31 - 1` that is 2·10⁹ iterations — minutes, not
  milliseconds.
""",
        ),
    ],
}


def range_bitwise_and(left: int, right: int) -> int:
    shift = 0

    # Discard bits that differ; whatever remains is the shared prefix.
    while left < right:
        left >>= 1
        right >>= 1
        shift += 1

    return left << shift


CASES = [
    ((5, 7), 4),
    ((0, 0), 0),
    ((1, 2147483647), 0),
    ((0, 1), 0),
    ((26, 30), 24),
    ((12, 15), 12),
    ((7, 7), 7),
    ((2147483646, 2147483647), 2147483646),
]


def solve(left: int, right: int) -> int:
    return range_bitwise_and(left, right)
