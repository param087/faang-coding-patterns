"""Sliding window templates.

Two shapes. A *fixed* window slides one element at a time. A *variable* window
grows on the right and shrinks on the left until an invariant holds again —
that shrink loop is the pattern, and `while` (not `if`) is what makes it work.
"""

from __future__ import annotations

from collections import Counter, defaultdict


def longest_unique_substring(s: str) -> int:
    """Longest substring with no repeated character.

    The invariant is "the window contains no duplicate". When the incoming
    character breaks it, shrink from the left until it holds again. Each index
    enters and leaves once, so it is O(n) despite the nested loop.
    """
    last_seen: dict[str, int] = {}
    left = 0
    best = 0

    for right, char in enumerate(s):
        # Jump the left edge past the previous occurrence, never backwards.
        if char in last_seen and last_seen[char] >= left:
            left = last_seen[char] + 1
        last_seen[char] = right
        best = max(best, right - left + 1)

    return best


def min_window(s: str, t: str) -> str:
    """Smallest substring of s containing every character of t, with counts.

    `missing` tracks how many required characters are still unmet. Counting
    *kinds* satisfied rather than total characters is what keeps the check
    O(1) instead of comparing two dicts on every step.
    """
    if not t or not s:
        return ""

    need = Counter(t)
    window: dict[str, int] = defaultdict(int)
    missing = len(need)
    best = (len(s) + 1, 0, 0)
    left = 0

    for right, char in enumerate(s):
        window[char] += 1
        if char in need and window[char] == need[char]:
            missing -= 1

        while missing == 0:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            drop = s[left]
            window[drop] -= 1
            if drop in need and window[drop] < need[drop]:
                missing += 1
            left += 1

    return "" if best[0] > len(s) else s[best[1] : best[2] + 1]


def subarrays_with_at_most_k_distinct(nums: list[int], k: int) -> int:
    """Count subarrays with at most k distinct values.

    Worth its own function because of the trick it enables: "exactly k" is
    `at_most(k) - at_most(k - 1)`. A window cannot maintain "exactly k"
    directly — shrinking is not monotone — so this subtraction is the
    standard way out, and it turns a Hard into two easy passes.
    """
    counts: dict[int, int] = defaultdict(int)
    left = 0
    total = 0

    for right, value in enumerate(nums):
        counts[value] += 1
        while len(counts) > k:
            counts[nums[left]] -= 1
            if counts[nums[left]] == 0:
                del counts[nums[left]]
            left += 1
        # Every subarray ending at `right` and starting at or after `left`.
        total += right - left + 1

    return total


def subarrays_with_exactly_k_distinct(nums: list[int], k: int) -> int:
    """Exactly k distinct, via the at-most-k subtraction."""
    if k == 0:
        return 0
    return subarrays_with_at_most_k_distinct(nums, k) - subarrays_with_at_most_k_distinct(
        nums, k - 1
    )


CASES = [
    (("abcabcbb",), 3),
    (("bbbbb",), 1),
    (("pwwkew",), 3),
    (("",), 0),
    (("dvdf",), 3),
]


def solve(s: str) -> int:
    return longest_unique_substring(s)


def check() -> None:
    for args, expected in CASES:
        assert longest_unique_substring(*args) == expected

    assert min_window("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window("a", "a") == "a"
    assert min_window("a", "aa") == ""
    assert min_window("", "a") == ""

    assert subarrays_with_at_most_k_distinct([1, 2, 1, 2, 3], 2) == 12
    assert subarrays_with_exactly_k_distinct([1, 2, 1, 2, 3], 2) == 7
    assert subarrays_with_exactly_k_distinct([1, 2, 1, 3, 4], 3) == 3
    assert subarrays_with_exactly_k_distinct([1, 2], 0) == 0
