"""Two Sum II - Input Array Is Sorted — LeetCode 167."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Sortedness turns the sum into a monotone dial: moving left raises it, moving right lowers it, so no pair is ever skipped.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A **sorted** array with exactly one pair summing to the target. Return their
positions, **1-indexed**, and use only constant extra space.

Two clarifications worth voicing: the indices are 1-based (the single most
common wrong submission), and "exactly one solution" means you never have to
decide between candidates.
""",
        ),
        (
            "The insight",
            """
Start at both ends. `nums[lo] + nums[hi]` is the largest sum still available
that uses `lo`, and the smallest still available that uses `hi`. So:

- sum too small → the only way up is `lo += 1`;
- sum too big → the only way down is `hi -= 1`.

Each move **discards a whole row or column** of the implicit n×n sum matrix,
and — this is the part to say out loud — the discarded pairs are all provably
non-solutions. Nothing is skipped. n moves total, O(1) space.
""",
        ),
        (
            "Why not binary search or a hash map",
            """
The array is sorted, so the reflex is binary search: for each `i`, look up
`target - nums[i]`. That works, but it is **O(n log n)** — strictly worse than
the pointers, and more code.

The hash map from Two Sum I is O(n) time but **O(n) space**, and the problem
explicitly forbids that. Sortedness is not decoration here; it is the entire
reason O(1) space is reachable.

Say both of these, then write the pointers. Reaching for the hash map on a
sorted array is the answer that reads as pattern-matching rather than thinking.
""",
        ),
    ],
}


def two_sum(numbers: list[int], target: int) -> list[int]:
    lo, hi = 0, len(numbers) - 1

    while lo < hi:
        total = numbers[lo] + numbers[hi]
        if total == target:
            return [lo + 1, hi + 1]  # 1-indexed
        if total < target:
            lo += 1  # only a bigger left value can help
        else:
            hi -= 1  # only a smaller right value can help

    return []


CASES = [
    (([2, 7, 11, 15], 9), [1, 2]),
    (([2, 3, 4], 6), [1, 3]),
    (([-1, 0], -1), [1, 2]),
    (([1, 2, 3, 4, 4, 9, 56, 90], 8), [4, 5]),  # duplicates, answer in the middle
    (([-10, -8, -2, 1, 3, 5], -5), [1, 6]),  # all negatives on the left
    (([0, 0, 3, 4], 0), [1, 2]),
    (([5, 25, 75], 100), [2, 3]),
]


def solve(numbers: list[int], target: int) -> list[int]:
    return two_sum(numbers, target)
