"""Search in Rotated Sorted Array — LeetCode 33."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "After any rotation at least one half is still properly sorted — find out which, then decide whether the target lives there.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A sorted array was rotated at some unknown pivot. Find a target's index, or
−1.

Ask: are values **distinct** (yes here — this decides whether O(log n) is even
possible); is the array guaranteed rotated (no, it may be in its original
order); return the index or a boolean.
""",
        ),
        (
            "The insight",
            """
Say this sentence before writing anything, because it *is* the solution:

> **After any rotation, at least one half of the array is still properly
> sorted.**

Compare `nums[low]` to `nums[mid]` to find out which half. Then check whether
the target falls inside that half's known range. If it does, search there; if
not, the other half must contain it.
""",
        ),
        (
            "The equals that matters",
            """
The test is `nums[low] <= nums[mid]`, **with** the equals.

On a two-element interval `mid == low`, so a strict `<` sends you down the
wrong branch. `[3, 1]` searching for 1 is the case that exposes it.
""",
        ),
        (
            "Dry run",
            """
`[4,5,6,7,0,1,2]`, target 0.

- `mid` = index 3, value 7. `nums[0]=4 <= 7` → **left half sorted**. Is 0 in
  `[4, 7)`? No → go right.
- Now `[0,1,2]`, `mid` = value 1. `nums[4]=0 <= 1` → left sorted. Is 0 in
  `[0, 1)`? Yes → go left.
- Found at index 4.
""",
        ),
        (
            "Follow-ups",
            """
- **Duplicates allowed** (Search in Rotated Sorted Array II). `[1,1,1,0,1]`
  makes the "which half is sorted" test **ambiguous** — `nums[low]`,
  `nums[mid]` and `nums[high]` can all be equal. The fix is to skip one
  element on a tie, and the worst case degrades to **O(n)**. Knowing that the
  guarantee *breaks* is the whole point of the follow-up.
- **Find Minimum in Rotated Sorted Array** — the pivot itself. Compare against
  `nums[high]`, never `nums[low]`: the right-end comparison is correct whether
  or not the array was actually rotated, so it needs no special case.
""",
        ),
    ],
}


def search(nums: list[int], target: int) -> int:
    low, high = 0, len(nums) - 1

    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid

        if nums[low] <= nums[mid]:  # `<=`: on a 2-element range mid == low
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:  # the right half is the sorted one
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1

    return -1


CASES = [
    (([4, 5, 6, 7, 0, 1, 2], 0), 4),
    (([4, 5, 6, 7, 0, 1, 2], 3), -1),
    (([1], 0), -1),
    (([1], 1), 0),
    (([3, 1], 1), 1),
    (([5, 1, 3], 3), 2),
    (([], 5), -1),
]


def solve(nums: list[int], target: int) -> int:
    return search(nums, target)
