"""First Missing Positive — LeetCode 41."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "The answer must lie in 1..n+1, so the array is its own hash table: park value v at index v-1 and find the first gap.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Given an unsorted array of arbitrary integers, return the smallest **positive**
integer that does not appear. Negatives, zeros and duplicates are all allowed
and all irrelevant to the answer.

The constraint is the problem: **O(n) time and O(1) auxiliary space.** With a
set it is four lines and nobody learns anything, so the interviewer is asking
for the in-place version and will say so. Confirm early that you may **mutate
the input** — the O(1) solution is impossible otherwise, and some interviewers
will refuse, in which case the honest answer is the set.
""",
        ),
        (
            "The insight",
            """
Two observations, and the second is the one people miss.

**The answer is bounded.** With `n` slots you can cover at most `1..n`, so the
answer is somewhere in `1..n+1`. If the array happens to be exactly a
permutation of `1..n`, the answer is `n+1`. Everything outside that window —
negatives, zeros, anything above `n` — cannot be the answer and cannot help
find it.

**A bounded key set means the array can be its own hash table.** You want a
lookup "is `v` present?" in O(1) with no extra memory, so define the slot for
`v` to be index `v - 1` and physically move each value there. After that pass,
`nums[i] != i + 1` identifies the first gap directly.

```
[3, 4, -1, 1]  ->  [1, -1, 3, 4]
 index 0 holds 1 ✓, index 1 should hold 2 but holds -1  ->  answer 2
```

The alternative in-place trick — negate `nums[v-1]` to mark `v` present, after
overwriting out-of-range values with `n+1` — is equally valid and slightly
shorter. It needs the input to be sign-free of meaning, and needs `abs()`
everywhere. Placement generalises better (it is cyclic sort), so prefer it.
""",
        ),
        (
            "Why the nested loop is still linear",
            """
A `while` inside a `for` reads as O(n²). It is not: **each iteration of the
`while` puts one value into its final home, and a value never leaves once
home**, so there are at most `n` swaps across the entire outer loop. Amortised
O(n). Interviewers ask this every single time — have the sentence ready.

The condition that makes it terminate is the one worth staring at:

```python
while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
```

The second clause compares **values**, not indices. Write `nums[i] != i + 1`
instead and `[1, 1]` loops forever, swapping two equal values back and forth.
Checking that the destination does not already hold the right value stops it
dead. That case is in the tests below.

One more trap: in the swap, precompute the destination.

```python
target = nums[i] - 1
nums[i], nums[target] = nums[target], nums[i]
```

Writing `nums[i], nums[nums[i] - 1] = nums[nums[i] - 1], nums[i]` is a real bug
in Python — the left-hand targets are assigned left to right, so `nums[i]` has
already changed by the time the second index expression is evaluated.
""",
        ),
    ],
}


def first_missing_positive(nums: list[int]) -> int:
    n = len(nums)

    for i in range(n):
        # Send nums[i] home; whatever comes back, send that home too.
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            target = nums[i] - 1  # precompute: the swap invalidates nums[i]
            nums[i], nums[target] = nums[target], nums[i]

    for i in range(n):
        if nums[i] != i + 1:
            return i + 1

    return n + 1  # the array was exactly a permutation of 1..n


CASES = [
    (([1, 2, 0],), 3),
    (([3, 4, -1, 1],), 2),
    (([7, 8, 9, 11, 12],), 1),  # nothing in range at all
    (([1, 1],), 2),  # duplicates: an index-based loop guard spins forever here
    (([1, 2, 3, 4, 5],), 6),  # a full permutation, so the answer is n + 1
    (([-1, -2],), 1),
    (([1],), 2),
    (([],), 1),
]


def solve(nums: list[int]) -> int:
    return first_missing_positive(list(nums))  # the algorithm mutates; keep CASES reusable
