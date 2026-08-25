"""Prefix sums and difference arrays.

One precomputation buys O(1) range queries. The variant that actually shows up
in interviews is not "sum of range [i, j]" — it is counting subarrays with a
property, which needs a hash map of prefixes seen so far.
"""

from __future__ import annotations

from collections import defaultdict


def build_prefix(nums: list[int]) -> list[int]:
    """`prefix[i]` is the sum of the first i elements, so prefix[0] == 0.

    The leading zero is what makes `sum(i..j) == prefix[j + 1] - prefix[i]`
    work without a special case for i == 0. Every off-by-one in this pattern
    comes from omitting it.
    """
    prefix = [0] * (len(nums) + 1)
    for i, value in enumerate(nums):
        prefix[i + 1] = prefix[i] + value
    return prefix


def subarray_sum_equals_k(nums: list[int], k: int) -> int:
    """Count subarrays summing to exactly k, in one pass.

    A subarray ending at i sums to k when `running - k` is a prefix we have
    already seen. Seeding the map with `{0: 1}` accounts for the subarray that
    starts at index 0.

    Note this handles negative numbers, which is exactly why a sliding window
    does *not* work here — a common wrong first answer.
    """
    seen: dict[int, int] = defaultdict(int)
    seen[0] = 1
    running = 0
    count = 0

    for value in nums:
        running += value
        count += seen[running - k]
        seen[running] += 1

    return count


def difference_array(length: int, updates: list[tuple[int, int, int]]) -> list[int]:
    """Apply many range increments in O(1) each, then materialise once.

    `updates` are inclusive `(start, end, delta)`. Marking +delta at `start`
    and -delta just past `end` means a single prefix sum at the end replays
    every update. This is the flight-bookings / car-pooling shape.
    """
    diff = [0] * (length + 1)

    for start, end, delta in updates:
        diff[start] += delta
        diff[end + 1] -= delta

    result: list[int] = []
    running = 0
    for i in range(length):
        running += diff[i]
        result.append(running)
    return result


CASES = [
    (([1, 1, 1], 2), 2),
    (([1, 2, 3], 3), 2),
    (([1, -1, 0], 0), 3),
    (([], 0), 0),
    (([3, 4, 7, 2, -3, 1, 4, 2], 7), 4),
]


def solve(nums: list[int], k: int) -> int:
    return subarray_sum_equals_k(nums, k)


def check() -> None:
    for args, expected in CASES:
        assert subarray_sum_equals_k(*args) == expected

    prefix = build_prefix([1, 2, 3, 4])
    assert prefix == [0, 1, 3, 6, 10]
    assert prefix[3] - prefix[1] == 5  # sum of nums[1..2]

    assert difference_array(5, [(1, 3, 2), (0, 1, 1)]) == [1, 3, 2, 2, 0]
    assert difference_array(3, []) == [0, 0, 0]
