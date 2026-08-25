"""Binary search on arrays.

One template, three bounds. Write the half-open version once, from memory,
and stop re-deriving the loop condition under pressure — that is where the
bugs come from.
"""

from __future__ import annotations


def lower_bound(nums: list[int], target: int) -> int:
    """First index whose value is >= target; len(nums) if none.

    The half-open invariant `[low, high)` is what makes this reliable:
    `low == high` terminates, `mid` can never equal `high`, and the answer is
    always `low`. Every other bound is a one-line variation of this.
    """
    low, high = 0, len(nums)

    while low < high:
        mid = (low + high) // 2
        if nums[mid] < target:
            low = mid + 1
        else:
            high = mid

    return low


def upper_bound(nums: list[int], target: int) -> int:
    """First index whose value is > target. `<=` instead of `<`."""
    low, high = 0, len(nums)

    while low < high:
        mid = (low + high) // 2
        if nums[mid] <= target:
            low = mid + 1
        else:
            high = mid

    return low


def search_range(nums: list[int], target: int) -> list[int]:
    """First and last index of target, or [-1, -1].

    Two calls to the bounds above. Writing this as one bespoke loop with
    extra flags is how people lose ten minutes on an easy question.
    """
    first = lower_bound(nums, target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]
    return [first, upper_bound(nums, target) - 1]


def search_rotated(nums: list[int], target: int) -> int:
    """Search a rotated sorted array with distinct values.

    At every step at least one half is properly sorted — compare `nums[low]`
    to `nums[mid]` to find out which. Then the target is in that half only if
    it falls inside its range; otherwise recurse on the other one.
    """
    low, high = 0, len(nums) - 1

    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid

        if nums[low] <= nums[mid]:  # left half is sorted
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:  # right half is sorted
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1

    return -1


def find_min_rotated(nums: list[int]) -> int:
    """Smallest value in a rotated sorted array.

    Compare against `nums[high]`, never `nums[low]`. On a non-rotated array
    comparing to `nums[low]` sends you the wrong way; comparing to the right
    end is correct in both cases, which is why this version has no special
    case for "not rotated at all".
    """
    low, high = 0, len(nums) - 1

    while low < high:
        mid = (low + high) // 2
        if nums[mid] > nums[high]:
            low = mid + 1  # minimum is strictly right of mid
        else:
            high = mid  # mid could be the minimum

    return nums[low]


CASES = [
    (([-1, 0, 3, 5, 9, 12], 9), 4),
    (([-1, 0, 3, 5, 9, 12], 2), -1),
    (([5], 5), 0),
    (([], 1), -1),
]


def solve(nums: list[int], target: int) -> int:
    index = lower_bound(nums, target)
    return index if index < len(nums) and nums[index] == target else -1


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected

    nums = [5, 7, 7, 8, 8, 10]
    assert search_range(nums, 8) == [3, 4]
    assert search_range(nums, 6) == [-1, -1]
    assert search_range([], 0) == [-1, -1]
    assert search_range([1], 1) == [0, 0]

    assert lower_bound([1, 3, 5], 0) == 0
    assert lower_bound([1, 3, 5], 6) == 3
    assert upper_bound([1, 2, 2, 3], 2) == 3

    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_rotated([1], 1) == 0

    assert find_min_rotated([3, 4, 5, 1, 2]) == 1
    assert find_min_rotated([4, 5, 6, 7, 0, 1, 2]) == 0
    assert find_min_rotated([11, 13, 15, 17]) == 11  # not rotated
    assert find_min_rotated([2, 1]) == 1
