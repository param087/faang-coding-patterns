"""3Sum — LeetCode 15."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Fix one element and the rest is 2Sum on a sorted array; the dedup is the actual difficulty.",
    "time": "O(n²)",
    "space": "O(1) extra, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Return every **unique** triple summing to zero. Order within a triple and
between triples does not matter, but duplicates must not appear.

Ask: may I sort (yes, unless indices are wanted), can the same element be
reused (no), are duplicate values in the input possible (yes — that is the
entire problem).
""",
        ),
        (
            "Brute force",
            """
Three nested loops plus a set to deduplicate: O(n³). At n = 3000 that is
2.7·10¹⁰ — dead on arrival, and the constraint says so.
""",
        ),
        (
            "The insight",
            """
Sort first. Then fix one element and the remainder becomes **2Sum on a sorted
array**, which converging two pointers solve in O(n).

Total O(n²) — 9·10⁶ at n = 3000, comfortable. The O(n log n) sort is free
against the O(n²) scan, which is worth saying because it justifies sorting at
all.
""",
        ),
        (
            "The dedup is the difficulty",
            """
Two separate skips, and they do different jobs:

- **Skip a repeated fixed element** (`nums[i] == nums[i-1]`), or the same
  triple family is emitted twice.
- **After recording a hit, skip repeats of the left pointer**, or `[0,0,0,0]`
  yields `[0,0,0]` several times.

Write both deliberately, talking through them as you go — adding them
afterwards in response to a failing test reads as debugging rather than
understanding.

The early `break` when `nums[i] > 0` is not just an optimisation: on a sorted
array nothing further can sum to zero, and saying so shows you are reasoning
about the sortedness rather than merely using it.
""",
        ),
        (
            "Follow-ups",
            """
- **3Sum Closest** — track the best difference instead of an exact zero.
- **4Sum** — one more loop, same dedup discipline, O(n³).
- **3Sum with a target other than zero** — identical; the `break` guard needs
  adjusting.
""",
        ),
    ],
}


def three_sum(nums: list[int]) -> list[list[int]]:
    nums = sorted(nums)
    result: list[list[int]] = []

    for i in range(len(nums) - 2):
        if nums[i] > 0:
            break  # sorted: nothing beyond here can reach zero
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # this fixed value was already handled

        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1  # skip duplicate left values

    return result


CASES = [
    (([-1, 0, 1, 2, -1, -4],), [[-1, -1, 2], [-1, 0, 1]]),
    (([0, 0, 0, 0],), [[0, 0, 0]]),
    (([0, 1, 1],), []),
    (([1, 2, -2, -1],), []),
    (([],), []),
]


def solve(nums: list[int]) -> list[list[int]]:
    return three_sum(nums)
