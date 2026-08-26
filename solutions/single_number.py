"""Single Number — LeetCode 136."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "XOR is its own inverse, so every value that appears twice annihilates itself and the fold leaves the loner behind.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Every element in the array appears exactly twice except one, which appears
once. Return that one — in **linear time and constant extra space**.

That second clause is the entire question. Without it this is a `Counter` and
nobody would ask it. So say the O(1)-space requirement out loud before you
write anything, because it is what rules out the two answers you thought of
first.

Worth asking: are the values bounded, and can they be negative? (They can —
which quietly kills "sum the distinct values, double it, subtract the total"
only if you get the arithmetic wrong; it survives, but XOR is cleaner.) Is the
array guaranteed non-empty? (Yes, and a length-1 array is a legal input.)
""",
        ),
        (
            "The insight",
            """
XOR has exactly the three properties you need:

- `a ^ a = 0` — a pair cancels itself;
- `a ^ 0 = a` — 0 is the identity, so cancelled pairs vanish;
- it is commutative and associative — so **the order does not matter**, and
  the pairs do not need to be adjacent, sorted, or found.

Fold XOR over the whole array and every duplicate quietly deletes itself:

```
1 ^ 2 ^ 1 ^ 3 ^ 2  =  (1 ^ 1) ^ (2 ^ 2) ^ 3  =  0 ^ 0 ^ 3  =  3
```

One accumulator register, one pass, no branch. Because the identity is 0, an
empty fold returns 0, which is the sensible degenerate answer.

The mental model to carry into the rest of this pattern: **XOR is addition
without carry, per bit column**. Each bit position independently counts its
1s mod 2, and a value seen twice contributes 0 to every column.
""",
        ),
        (
            "Follow-ups — and they will ask one",
            """
136 is the easy door into a family, and the interviewer usually walks through
it:

- **[Single Number II](../single-number-ii/)** — everything appears three
  times except one. XOR fails outright, because mod 2 no longer cancels a
  triple. You count each bit column mod 3 instead.
- **[Single Number III](../single-number-iii/)** — *two* elements appear once.
  The fold gives you `x ^ y`; you then split the array on any bit where they
  differ.
- **[Missing Number](../missing-number/)** — XOR the values *and* the indices
  together; the same cancellation finds the gap.
- **Streaming**: XOR is a single register updated per element, so it works on
  a stream you cannot re-read or store. A hash set does not.

The generalisation worth naming: for "every element appears `k` times except
one", count each bit column mod `k`. XOR is exactly that construction for
`k = 2`, which is why it collapses to one operator.
""",
        ),
    ],
}


def single_number(nums: list[int]) -> int:
    loner = 0

    for num in nums:
        loner ^= num  # pairs cancel; order is irrelevant

    return loner


CASES = [
    (([2, 2, 1],), 1),
    (([4, 1, 2, 1, 2],), 4),
    (([1],), 1),
    (([0, 1, 0],), 1),  # the answer sits next to a zero
    (([-1, -1, -2],), -2),  # negatives XOR fine in two's complement
    (([5, 5, -7, -7, 3],), 3),
    (([],), 0),  # the fold identity, for a degenerate input
]


def solve(nums: list[int]) -> int:
    return single_number(nums)
