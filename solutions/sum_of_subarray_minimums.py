"""Sum of Subarray Minimums — LeetCode 907."""

from __future__ import annotations

META = {
    "pattern": "monotonic-stack",
    "insight": "Stop enumerating subarrays; ask each element how many subarrays it is the minimum of, which is a span times a span.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Sum `min(subarray)` over **every** contiguous subarray, modulo 10⁹ + 7.

There are n(n+1)/2 subarrays; at n = 3·10⁴ that is 4.5·10⁸ of them, so even an
O(n²) loop that computes each minimum in O(1) is too slow — and the modulus in
the statement is a hint that the true answer is enormous, not that the
algorithm is arithmetic-heavy.

Ask whether values can repeat. They can, and that single fact is what makes
this Medium rather than Easy.
""",
        ),
        (
            "The insight",
            """
Invert the sum. Instead of "for each subarray, find its minimum", ask **for
each element, how many subarrays have it as the minimum** — then the answer is

```
sum over i of  arr[i] * count(i)
```

Element `i` is the minimum of exactly the subarrays that stretch left no
further than the previous smaller element and right no further than the next
smaller one. If those boundaries are at `left` and `right` (exclusive), the
count is a product of two independent choices:

```
(i - left) * (right - i)
```

Previous-smaller and next-smaller for every index is the monotonic stack, one
pass. And as in Largest Rectangle in Histogram, both boundaries of `i` are
known **at the moment `i` is popped**: whoever pops it is its right boundary,
and whatever is under it is its left one.
""",
        ),
        (
            "The tie-break that decides it",
            """
With duplicates, "previous smaller" and "next smaller" both being strict makes
elements fight over the same subarray, and both being loose makes them each
claim it. On `[2, 2]` you get 8 or 4 instead of 6.

The fix is to make the comparison **asymmetric**: strictly smaller on one side,
smaller-or-equal on the other. Here the stack keeps strictly increasing values,
so:

- left boundary = previous **strictly** smaller;
- right boundary = next smaller **or equal** (the pop test is `>=`).

Every subarray is then charged to the leftmost of its tied minima, exactly
once. Verify on `[2, 2]`: index 0 owns `[2]`, index 1 owns `[2]` and `[2, 2]`,
total 6. If you cannot get this right at the whiteboard, write out the two
`for` loops with `prev_less` / `next_less_or_equal` explicitly — clarity beats
a clever one-pass version you cannot defend.

The `right == n` sentinel drains the stack at the end, so trailing elements
that never get popped are still measured, with `n` as their right boundary.
""",
        ),
    ],
}

MOD = 10**9 + 7


def sum_subarray_mins(arr: list[int]) -> int:
    n = len(arr)
    total = 0
    stack: list[int] = []  # indices, values strictly increasing bottom -> top

    for right in range(n + 1):  # right == n is the draining sentinel
        # `>=` here makes the right boundary "next smaller or equal"; the stack
        # staying strictly increasing makes the left one "previous strictly smaller".
        while stack and (right == n or arr[stack[-1]] >= arr[right]):
            mid = stack.pop()
            left = stack[-1] if stack else -1
            total = (total + arr[mid] * (mid - left) * (right - mid)) % MOD
        stack.append(right)

    return total


CASES = [
    (([3, 1, 2, 4],), 17),
    (([11, 81, 94, 43, 3],), 444),
    # Duplicates: the case that separates a correct tie-break from a plausible one.
    (([2, 2],), 6),
    (([2, 2, 2],), 12),
    (([1, 2, 3, 4],), 20),
    (([4, 3, 2, 1],), 20),
    (([1],), 1),
    (([],), 0),
    # 500_500 subarrays all with the same minimum: 30000 * 500500 exceeds the modulus.
    (([30_000] * 1_000,), 14_999_895),
]


def solve(arr: list[int]) -> int:
    return sum_subarray_mins(arr)
