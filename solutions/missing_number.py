"""Missing Number — LeetCode 268."""

from __future__ import annotations

META = {
    "pattern": "bit-manipulation",
    "insight": "XOR the values against the indices 0..n: every number that is present cancels itself and only the absent one survives.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
`nums` holds `n` **distinct** numbers drawn from `[0, n]` — that is `n + 1`
possible values for `n` slots — so exactly one is missing. Return it.

Ask two things:

1. **Is O(1) extra space required?** It is the stated follow-up, and it is the
   only reason this is not a one-line `set` difference.
2. **May I mutate the input?** If yes, cyclic sort (place each value `v` at
   index `v`, then scan for the mismatch) is a legitimate O(n)/O(1) answer and
   generalises to the harder variants where numbers repeat.

Note the range is `[0, n]` inclusive, not `[1, n]`. Half the wrong answers to
this problem are off by one because of that.
""",
        ),
        (
            "The insight",
            """
The indices `0..n-1` plus the sentinel `n` are exactly the candidate values.
So XOR **the indices and the values together** in one pass:

```python
missing = len(nums)
for i, num in enumerate(nums):
    missing ^= i ^ num
```

Every value that is actually present appears once as a value and once as an
index, and `a ^ a = 0` deletes the pair. Start the accumulator at `n` because
that index does not exist in the loop. What is left is the number that never
turned up as a value.

Same cancellation as [Single Number](../single-number/), but here you supply
the missing half of each pair yourself.
""",
        ),
        (
            "Sum vs XOR — the argument to have ready",
            """
The Gauss answer is equally valid and usually the first one out of people's
mouths:

```
missing = n * (n + 1) // 2 - sum(nums)
```

One multiplication, one pass. In Python it is flawless, because integers do
not overflow.

**In Java or C++ it can overflow.** `n·(n+1)/2` exceeds a signed 32-bit int
once `n` is around 65 535, and the running `sum` overflows at roughly the same
point. LeetCode caps `n` at 10⁴ so it never bites there, but "what if n is
10⁶?" is precisely the follow-up an interviewer uses to see whether you
noticed. XOR never overflows: it stays inside 32 bits by construction.

The answer worth giving: *"Sum is fine and I'd write it in Python; XOR is what
I'd ship in Java, because it has no width assumption at all."*

**Other angles they may push you towards:**

- **Sorted input?** Binary search for the first index where `nums[i] != i`;
  O(log n).
- **Numbers may repeat, or several are missing?** XOR collapses, because the
  cancellation no longer isolates one value. Switch to cyclic sort or negation
  marking — the machinery of
  [First Missing Positive](../first-missing-positive/).
""",
        ),
    ],
}


def missing_number(nums: list[int]) -> int:
    missing = len(nums)  # index n has no slot in the loop below

    for i, num in enumerate(nums):
        missing ^= i ^ num  # present values cancel against their own index

    return missing


CASES = [
    (([3, 0, 1],), 2),
    (([0, 1],), 2),  # the missing one is n itself
    (([1, 0],), 2),
    (([1],), 0),  # missing zero, the off-by-one killer
    (([0],), 1),
    (([9, 6, 4, 2, 3, 5, 7, 0, 1],), 8),
    (([],), 0),  # n = 0: the range is just [0, 0]
]


def solve(nums: list[int]) -> int:
    return missing_number(nums)
