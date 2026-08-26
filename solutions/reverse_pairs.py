"""Reverse Pairs — LeetCode 493."""

from __future__ import annotations

META = {
    "pattern": "divide-and-conquer",
    "insight": "Same merge-sort inversion count, except the predicate a > 2b no longer falls out of the merge comparison — it needs its own pass.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Count pairs `i < j` with `nums[i] > 2 · nums[j]`.

Ask whether the values can be negative — they can, down to `-2³¹`, and that
kills the two shortcuts people reach for first: dividing by two (`nums[i] / 2
> nums[j]` is wrong for odd values, and integer division truncates towards
zero, so it is wrong in a *different* way on negatives) and doubling in a
32-bit type (`2 · 2³¹` overflows). In Python neither bites, but say it —
in C++ or Java `2L * nums[j]` is the fix and interviewers look for it.
""",
        ),
        (
            "The insight",
            """
It is Count of Smaller Numbers After Self with a different predicate, so the
skeleton is the same: a pair `i < j` is separated by exactly one merge in the
recursion, so if each merge counts the pairs it separates, the totals sum to
the answer with nothing double-counted.

Inside one merge both halves are sorted. Sweep a pointer `j` over the right
half that never resets:

```python
j = 0
for value in left:
    while j < len(right) and value > 2 * right[j]:
        j += 1
    total += j
```

`left` is ascending, so the set of qualifying right-half elements only grows —
`j` moves forward at most `len(right)` times across the entire loop, giving a
linear pass. That linear pass is what keeps the level at O(n) and the whole
thing at O(n log n).
""",
        ),
        (
            "The pitfall: counting and merging are two separate passes",
            """
In the classic inversion count you can fold the counting into the merge
comparison, because the thing you compare (`a > b`) is the thing you count.
Here you compare `a > b` to merge but count `a > 2b`, and the two pointers
advance at different rates. Trying to run one loop that does both is the most
common way this problem goes wrong — the counter ends up wrong on the first
input with a value between `b` and `2b`.

So: **count first over both sorted halves, then merge**. Two clean linear
passes, no shared state. The extra pass changes nothing asymptotically.

Two more details worth naming:

- Count *before* merging, or count using the two halves as they were. Once the
  halves are interleaved, "which side did this come from" is gone.
- `[-5, -5]` is a valid reverse pair, since `-5 > -10`. Any implementation
  that assumes positives — halving, or an early `if nums[i] <= 0: continue` —
  reports 0. It is the single best test case to write down first.
""",
        ),
    ],
}


def reverse_pairs(nums: list[int]) -> int:
    def sort_and_count(values: list[int]) -> tuple[list[int], int]:
        if len(values) <= 1:
            return values, 0

        mid = len(values) // 2
        left, left_count = sort_and_count(values[:mid])
        right, right_count = sort_and_count(values[mid:])
        total = left_count + right_count

        # Pass one: count. `j` never resets, because `left` is ascending.
        j = 0
        for value in left:
            while j < len(right) and value > 2 * right[j]:
                j += 1
            total += j

        # Pass two: merge. Kept separate — the two predicates advance differently.
        merged: list[int] = []
        i = j = 0
        while i < len(left) or j < len(right):
            if j == len(right) or (i < len(left) and left[i] <= right[j]):
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        return merged, total

    return sort_and_count(nums)[1]


CASES = [
    (([1, 3, 2, 3, 1],), 2),
    (([2, 4, 3, 5, 1],), 3),
    (([5, 4, 3, 2, 1],), 4),
    (([],), 0),
    (([1],), 0),
    # Negatives: -5 > 2 * -5 = -10, so this is a pair. Halving instead of
    # doubling, or skipping non-positive values, reports 0 here.
    (([-5, -5],), 1),
    (([-2147483648, -2147483648],), 1),
    (([0, 0, 0],), 0),
]


def solve(nums: list[int]) -> int:
    return reverse_pairs(list(nums))
