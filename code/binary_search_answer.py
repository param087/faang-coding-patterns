"""Binary search on the answer (parametric search).

The step most candidates never take. You are not searching an array — you are
searching the *range of possible answers*, and the array is only used to
answer "is this candidate feasible?".

It applies whenever feasibility is monotone: if speed 5 works, so does 6.
"""

from __future__ import annotations

import math


def min_eating_speed(piles: list[int], hours: int) -> int:
    """Smallest bananas-per-hour that finishes every pile within `hours`.

    The template. Note the shape: a `feasible` predicate over a candidate
    answer, then a lower-bound binary search over `[1, max(piles)]`. Nothing
    about the array is searched; only the answer space is.
    """

    def feasible(speed: int) -> bool:
        # ceil division: a partial pile still costs a whole hour.
        return sum(math.ceil(pile / speed) for pile in piles) <= hours

    low, high = 1, max(piles)
    while low < high:
        mid = (low + high) // 2
        if feasible(mid):
            high = mid  # mid works; look for something smaller
        else:
            low = mid + 1

    return low


def ship_within_days(weights: list[int], days: int) -> int:
    """Smallest ship capacity that ships all packages, in order, within `days`.

    The bounds are the interesting part. The lower bound is `max(weights)` —
    any smaller capacity cannot carry the heaviest single package at all —
    and the upper bound is `sum(weights)`, one day. Picking 1 as the lower
    bound would make `feasible` loop forever.
    """

    def feasible(capacity: int) -> bool:
        used, load = 1, 0
        for weight in weights:
            if load + weight > capacity:
                used += 1
                load = 0
            load += weight
        return used <= days

    low, high = max(weights), sum(weights)
    while low < high:
        mid = (low + high) // 2
        if feasible(mid):
            high = mid
        else:
            low = mid + 1

    return low


def split_array_largest_sum(nums: list[int], k: int) -> int:
    """Split into k contiguous subarrays, minimising the largest subarray sum.

    Reads like a DP problem, and the O(n²k) DP is a valid answer. The
    binary-search version is O(n log(sum)) and much shorter: guess the
    largest allowed sum, greedily cut whenever you would exceed it, and check
    whether you used at most k pieces.
    """

    def feasible(limit: int) -> bool:
        pieces, running = 1, 0
        for value in nums:
            if running + value > limit:
                pieces += 1
                running = 0
            running += value
        return pieces <= k

    low, high = max(nums), sum(nums)
    while low < high:
        mid = (low + high) // 2
        if feasible(mid):
            high = mid
        else:
            low = mid + 1

    return low


CASES = [
    (([3, 6, 7, 11], 8), 4),
    (([30, 11, 23, 4, 20], 5), 30),
    (([30, 11, 23, 4, 20], 6), 23),
    (([1], 1), 1),
]


def solve(piles: list[int], hours: int) -> int:
    return min_eating_speed(piles, hours)


def check() -> None:
    for args, expected in CASES:
        assert min_eating_speed(*args) == expected

    assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert ship_within_days([3, 2, 2, 4, 1, 4], 3) == 6
    assert ship_within_days([1, 2, 3, 1, 1], 4) == 3

    assert split_array_largest_sum([7, 2, 5, 10, 8], 2) == 18
    assert split_array_largest_sum([1, 2, 3, 4, 5], 2) == 9
    assert split_array_largest_sum([1, 4, 4], 3) == 4
