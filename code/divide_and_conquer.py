"""Divide and conquer.

Split, solve the halves, combine. The interesting problems are the ones where
the *combine* step does real work — counting inversions during a merge — and
the ones where you only need to recurse into **one** half, which is what makes
quickselect O(n) instead of O(n log n).
"""

from __future__ import annotations

import random


def quickselect(nums: list[int], k: int) -> int:
    """The k-th largest value. O(n) expected.

    The whole idea: after partitioning, you know which side the answer is on,
    so you discard the other instead of sorting it. That turns the recurrence
    from T(n) = 2T(n/2) + n into T(n) = T(n/2) + n, which sums to O(n).

    The random pivot matters. A fixed pivot on sorted input is O(n²), and
    LeetCode's test cases include sorted input for exactly that reason.
    """
    values = nums[:]  # don't mutate the caller's list
    target = len(values) - k  # k-th largest == this index when sorted ascending
    low, high = 0, len(values) - 1

    while low <= high:
        pivot_index = random.randint(low, high)
        values[pivot_index], values[high] = values[high], values[pivot_index]
        pivot = values[high]

        store = low
        for i in range(low, high):
            if values[i] < pivot:
                values[store], values[i] = values[i], values[store]
                store += 1
        values[store], values[high] = values[high], values[store]

        if store == target:
            return values[store]
        if store < target:
            low = store + 1
        else:
            high = store - 1

    raise ValueError("k out of range")


def count_smaller_after_self(nums: list[int]) -> list[int]:
    """For each index, how many later values are smaller. O(n log n).

    A merge sort where the combine step counts. When an element from the right
    half is emitted before one from the left, it is smaller than every
    remaining left element — so credit them all at once. Indices are carried
    alongside the values so the answer lands in the right slot.
    """
    counts = [0] * len(nums)
    indexed = list(enumerate(nums))

    def sort(items: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if len(items) <= 1:
            return items
        mid = len(items) // 2
        left = sort(items[:mid])
        right = sort(items[mid:])

        merged: list[tuple[int, int]] = []
        i = j = 0
        while i < len(left) and j < len(right):
            if right[j][1] < left[i][1]:
                merged.append(right[j])
                j += 1
            else:
                # Everything already taken from the right is smaller than this.
                counts[left[i][0]] += j
                merged.append(left[i])
                i += 1
        while i < len(left):
            counts[left[i][0]] += j
            merged.append(left[i])
            i += 1
        merged.extend(right[j:])
        return merged

    sort(indexed)
    return counts


def max_subarray(nums: list[int]) -> int:
    """Largest contiguous sum — Kadane, which is the O(n) answer.

    Included here because the divide-and-conquer version (best-left,
    best-right, best-crossing) is a classic O(n log n) exercise, and the point
    worth making is that D&C is not always the right tool. Kadane wins.
    """
    best = current = nums[0]
    for value in nums[1:]:
        # Either extend the running subarray or start fresh here.
        current = max(value, current + value)
        best = max(best, current)
    return best


CASES = [
    (([3, 2, 1, 5, 6, 4], 2), 5),
    (([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4),
    (([1], 1), 1),
    (([2, 1], 2), 1),
]


def solve(nums: list[int], k: int) -> int:
    return quickselect(nums, k)


def check() -> None:
    for args, expected in CASES:
        assert quickselect(*args) == expected

    # Sorted input: the case a fixed pivot degrades on.
    assert quickselect(list(range(200)), 1) == 199
    assert quickselect(list(range(200)), 200) == 0

    assert count_smaller_after_self([5, 2, 6, 1]) == [2, 1, 1, 0]
    assert count_smaller_after_self([-1]) == [0]
    assert count_smaller_after_self([-1, -1]) == [0, 0]
    assert count_smaller_after_self([]) == []

    assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert max_subarray([-1]) == -1
    assert max_subarray([5, 4, -1, 7, 8]) == 23
