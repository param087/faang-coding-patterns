"""Sorting and custom comparators.

The sort itself is one line. What earns the round is choosing the key, knowing
when a comparison-free sort applies, and being able to say why a comparator is
a valid ordering when the answer is not simply "ascending".
"""

from __future__ import annotations

from collections import Counter
from functools import cmp_to_key


def largest_number(nums: list[int]) -> str:
    """Arrange integers to form the largest possible number.

    The key insight is that the ordering is *not* numeric or lexicographic:
    `a` comes before `b` when `a + b > b + a` as strings ("9" before "34"
    because "934" > "349"). Python needs `cmp_to_key` for this because the
    comparison is pairwise and cannot be expressed as a per-item key.
    """
    if not nums:
        return "0"

    def compare(a: str, b: str) -> int:
        if a + b > b + a:
            return -1
        return 1 if a + b < b + a else 0

    ordered = sorted((str(n) for n in nums), key=cmp_to_key(compare))
    result = "".join(ordered)
    return "0" if result[0] == "0" else result  # all zeros collapse to "0"


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """The k most frequent values, in O(n) with bucket sort.

    A heap gives O(n log k) and is the usual answer. Bucketing by frequency is
    O(n) and available because a frequency can never exceed n — worth offering
    once you have given the heap version.
    """
    counts = Counter(nums)
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for value, frequency in counts.items():
        buckets[frequency].append(value)

    result: list[int] = []
    for frequency in range(len(buckets) - 1, 0, -1):
        for value in buckets[frequency]:
            result.append(value)
            if len(result) == k:
                return result
    return result


def merge_sort(nums: list[int]) -> list[int]:
    """Stable O(n log n) sort, written out because interviewers ask.

    Also the substrate for counting inversions and Count of Smaller Numbers
    After Self — the merge step is where you learn how many elements from the
    right half jumped ahead of an element in the left.
    """
    if len(nums) <= 1:
        return nums[:]

    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])

    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        # `<=` keeps equal elements in their original order: stability.
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def sort_by_parity(nums: list[int]) -> list[int]:
    """Evens before odds, in place, O(n) — no sort needed.

    A reminder that "sort by X" often means "partition by X", and a partition
    is linear. Reaching for `sorted(key=...)` here is an O(n log n) answer to
    an O(n) question.
    """
    write = 0
    for i, value in enumerate(nums):
        if value % 2 == 0:
            nums[write], nums[i] = nums[i], nums[write]
            write += 1
    return nums


CASES = [
    (([10, 2],), "210"),
    (([3, 30, 34, 5, 9],), "9534330"),
    (([0, 0],), "0"),
    (([1],), "1"),
    (([],), "0"),
]


def solve(nums: list[int]) -> str:
    return largest_number(nums)


def check() -> None:
    for args, expected in CASES:
        assert largest_number(*args) == expected

    assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
    assert top_k_frequent([1], 1) == [1]

    assert merge_sort([5, 2, 3, 1]) == [1, 2, 3, 5]
    assert merge_sort([]) == []
    assert merge_sort([1]) == [1]

    result = sort_by_parity([3, 1, 2, 4])
    assert all(v % 2 == 0 for v in result[:2])
    assert all(v % 2 == 1 for v in result[2:])
