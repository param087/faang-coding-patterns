"""Running Sum of 1d Array — LeetCode 1480."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "Every prefix-sum problem starts here: one pass carrying a total, and the only real decision is where the leading zero goes.",
    "time": "O(n)",
    "space": "O(1) extra, or O(n) if you must not touch the input",
    "sections": [
        (
            "What it asks",
            """
Return the array whose `i`-th entry is `nums[0] + ... + nums[i]`.

There is no algorithm to find here. What the interviewer is watching for is
whether you reach for `accumulate` and move on, or whether you stall. Treat it
as a warm-up and spend the saved minute on the follow-up.

Ask one thing only: **may I write into `nums`?** If yes the answer is O(1)
extra space; if not, allocate.
""",
        ),
        (
            "The insight",
            """
`total += value` and append. In Python that is `list(accumulate(nums))`, one
line, and saying so is worth more than typing the loop — it shows you know the
stdlib.

The loop is written out below anyway, because in a Java or C++ round you write
the loop, and because the in-place variant is the follow-up.
""",
        ),
        (
            "The convention that decides every later problem",
            """
This problem hands you the **inclusive** running sum: `sums[i]` includes
`nums[i]`, and the array has length `n`.

Almost every harder prefix-sum problem — Range Sum Query, Contiguous Array,
Subarray Sum Equals K — wants the **exclusive** form instead:

```
prefix[0] = 0
prefix[i] = nums[0] + ... + nums[i - 1]     # length n + 1
```

with a leading zero. That zero is what makes `sum(l..r) = prefix[r+1] -
prefix[l]` work with **no special case for `l == 0`**, and it is why hash-map
variants seed their map with `{0: -1}`.

Pick the convention deliberately and say which one you are using before you
write the loop. Mixing the two mid-problem is the single most common source of
off-by-one bugs in this pattern.
""",
        ),
    ],
}


def running_sum(nums: list[int]) -> list[int]:
    """Inclusive running sum. Equivalent to `list(accumulate(nums))`."""
    sums: list[int] = []
    total = 0
    for value in nums:
        total += value
        sums.append(total)
    return sums


def running_sum_in_place(nums: list[int]) -> list[int]:
    """O(1) extra space — the follow-up. Overwrites `nums`."""
    for i in range(1, len(nums)):
        nums[i] += nums[i - 1]
    return nums


def exclusive_prefix(nums: list[int]) -> list[int]:
    """The form the rest of the pattern actually uses: length n + 1, leading 0."""
    prefix = [0] * (len(nums) + 1)
    for i, value in enumerate(nums):
        prefix[i + 1] = prefix[i] + value
    return prefix


CASES = [
    (([1, 2, 3, 4],), [1, 3, 6, 10]),
    (([1, 1, 1, 1, 1],), [1, 2, 3, 4, 5]),
    (([3, 1, 2, 10, 1],), [3, 4, 6, 16, 17]),
    (([-1, -2, 3, -4],), [-1, -3, 0, -4]),
    (([0, 0, 0],), [0, 0, 0]),
    (([5],), [5]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return running_sum(nums)  # does not mutate, so CASES are reusable


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

        # The in-place variant must agree, and it is allowed to eat its input.
        scratch = list(args[0])
        assert running_sum_in_place(scratch) == expected

        # The exclusive form drops the leading zero to give the inclusive one.
        prefix = exclusive_prefix(args[0])
        assert len(prefix) == len(args[0]) + 1
        assert prefix[0] == 0
        assert prefix[1:] == expected

    # sum(l..r) = prefix[r + 1] - prefix[l], with no branch at l == 0.
    nums = [4, -1, 9, 0, 3, -7]
    prefix = exclusive_prefix(nums)
    for left in range(len(nums)):
        for right in range(left, len(nums)):
            assert prefix[right + 1] - prefix[left] == sum(nums[left : right + 1])
