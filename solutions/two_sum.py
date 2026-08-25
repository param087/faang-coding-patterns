"""Two Sum — LeetCode 1."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "Instead of searching forward for a partner, ask whether the partner has already gone past.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given an array of integers and a target, return the **indices** of the two
values that sum to the target. Exactly one answer exists, and you may not use
the same element twice.

Ask before starting: can values be negative (yes), can they repeat (yes), and
is the array sorted (no — if it were, two pointers would be better).
""",
        ),
        (
            "Brute force, and why it fails",
            """
Check every pair: two nested loops, O(n²). At n = 10⁴ that is 10⁸ operations —
borderline, and the constraint is hinting you can do better.

Say the number rather than the word "slow". It is the number that justifies
what comes next.
""",
        ),
        (
            "The insight",
            """
The brute force asks, for each element, "is there a later element that
completes it?" — which requires looking forward.

Flip it. For each element ask "have I **already seen** the number that
completes this one?" That question is a hash-map lookup, so one pass suffices.

The ordering inside the loop matters: check for the complement **before**
inserting the current value. Inserting first lets a value pair with itself,
which fails on `nums = [3, 3], target = 6`.
""",
        ),
        (
            "Edge cases",
            """
- `[3, 3], 6` — the self-pairing case. This is the one that catches an
  insert-then-check ordering.
- Negative values and zero, both allowed.
- An empty array, which returns nothing.
""",
        ),
        (
            "Follow-ups",
            """
- **"What if the array were sorted?"** — this is asked almost every time. Two
  pointers converging from the ends, O(n) time and **O(1) space**. That space
  improvement is the point of the question.
- **"What if you needed all pairs, not one?"** — same map, but keep collecting
  rather than returning early, and handle duplicate pairs.
- **Three Sum** — fix one element and run this inside it.
""",
        ),
    ],
}


def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}  # value -> index

    for i, value in enumerate(nums):
        complement = target - value
        # Check before inserting, or a value pairs with itself.
        if complement in seen:
            return [seen[complement], i]
        seen[value] = i

    return []


CASES = [
    (([2, 7, 11, 15], 9), [0, 1]),
    (([3, 2, 4], 6), [1, 2]),
    (([3, 3], 6), [0, 1]),
    (([-1, -2, -3, -4], -6), [1, 3]),
    (([0, 4, 3, 0], 0), [0, 3]),
    (([], 0), []),
]


def solve(nums: list[int], target: int) -> list[int]:
    return two_sum(nums, target)
