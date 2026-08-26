"""Find Minimum in Rotated Sorted Array — LeetCode 153."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "Compare the midpoint with the right end, never the left — that one choice makes the unrotated array need no special case.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A sorted array of distinct values was rotated an unknown number of times.
Return the minimum in O(log n).

Confirm two things: values are **distinct** (with duplicates this is LeetCode
154 and O(log n) is impossible), and the rotation may be by **zero** — the
array can still be in sorted order. That second one is where most attempts
break.
""",
        ),
        (
            "The insight",
            """
The minimum is the pivot: the single place where the array steps *down*.
Everything left of the pivot is greater than everything right of it.

Compare `nums[mid]` with `nums[high]`:

- `nums[mid] > nums[high]` — the step down is strictly to the right of `mid`,
  so `low = mid + 1`.
- otherwise `mid` is on the same run as `high`, so the pivot is at `mid` or
  left of it: `high = mid`.

Loop `while low < high`, return `nums[low]`. There is no equality case,
because distinct values mean `nums[mid] == nums[high]` only when
`mid == high`, which the loop condition already excludes.
""",
        ),
        (
            "Why nums[high], never nums[low]",
            """
Comparing against `nums[low]` is the version that needs patching. On
`[1, 2, 3]` — rotated by zero — `nums[mid] >= nums[low]` is true, and the
"left half is sorted, go right" rule sends you away from the answer, which is
at index 0. You end up bolting on `if nums[low] < nums[high]: return nums[low]`
to rescue it.

`nums[high]` needs no such rescue. If the array is not rotated then
`nums[mid] <= nums[high]` at every step, `high` walks down to 0, and the answer
is right. One comparison, no branches, no early exit.

**Follow-up, Find Minimum II (duplicates).** `[3, 3, 1, 3]` versus
`[3, 1, 3, 3]`: the mid and the right end both read 3 and the two arrays are
indistinguishable at that point. The fix is `high -= 1` on a tie — safe,
because `nums[high]` is duplicated at `mid` and so is never uniquely the
minimum — but the worst case degrades to **O(n)**. Being able to say *why* the
guarantee is lost matters more than the patch.
""",
        ),
    ],
}


def find_min(nums: list[int]) -> int:
    low, high = 0, len(nums) - 1

    while low < high:
        mid = (low + high) // 2
        if nums[mid] > nums[high]:
            low = mid + 1  # the step down is strictly right of mid
        else:
            high = mid  # mid is on the same run as high — pivot is at mid or left

    return nums[low]


CASES = [
    (([3, 4, 5, 1, 2],), 1),
    (([4, 5, 6, 7, 0, 1, 2],), 0),
    (([11, 13, 15, 17],), 11),
    (([2, 1],), 1),
    (([1, 2],), 1),
    (([1],), 1),
    (([5, 1, 2, 3, 4],), 1),
    (([2, 3, 4, 5, 1],), 1),
]


def solve(nums: list[int]) -> int:
    return find_min(nums)
