"""Next Permutation — LeetCode 31."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "The longest non-increasing suffix is already maximal, so the change happens at the element just before it — and must be minimal.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Rearrange the array in place into the next lexicographically greater
permutation of the same multiset. If none exists — the array is already the
largest arrangement — wrap round to the smallest, i.e. sorted ascending.

Clarify two things: duplicates are allowed (`[1,1,5]` → `[1,5,1]`), and "next"
means next among **permutations of these exact values**, not the next larger
number you could form. And it must be O(1) space, which rules out generating
permutations.
""",
        ),
        (
            "The insight",
            """
Scan from the right for the longest **non-increasing** suffix. That suffix is
already the largest arrangement of its own values, so nothing you do inside it
can increase the array. The element immediately before it — call it the
**pivot** at index `i`, where `nums[i] < nums[i+1]` — is the leftmost position
that has to change.

To keep the increase as small as possible:

1. Swap the pivot with the **smallest value in the suffix that still exceeds
   it**. Because the suffix is non-increasing, that is the *rightmost* element
   greater than the pivot — found by walking left from the end.
2. The suffix is still non-increasing after the swap (the incoming value sits
   in the same order slot the outgoing one did), so **reverse** it to get the
   smallest tail. Reversing, not sorting: O(n) not O(n log n).

If no pivot exists, the whole array is non-increasing — reverse it all, which
is exactly the required wrap-round. That case needs no separate branch.
""",
        ),
        (
            "The detail that decides it",
            """
Both comparisons need the right strictness, and duplicates are what expose a
wrong one.

- Finding the pivot: walk left while `nums[i] >= nums[i+1]`. Using `>` stops
  early on a plateau — `[2,3,3,1]` would pick `i = 1` instead of `i = 0` and
  produce a permutation that is not the *next* one.
- Finding the swap partner: walk left while `nums[j] <= nums[i]`, so the
  landing spot is **strictly** greater. Using `<` lets you swap with an equal
  value, which leaves the array unchanged in value order and returns the same
  permutation.

Dry run `[2,3,3,1]`: suffix `[3,3,1]` is non-increasing, pivot is `2` at index
0. Rightmost value greater than 2 is the `3` at index 2. Swap → `[3,3,2,1]`.
Reverse the suffix → **`[3,1,2,3]`**. Correct: 2331 → 3123.

Dry run `[5,4,7,5,3,2]`: pivot is `4` at index 1 (suffix `[7,5,3,2]`).
Rightmost value greater than 4 is the `5` at index 3. Swap → `[5,5,7,4,3,2]`,
reverse from index 2 → **`[5,5,2,3,4,7]`**.

`[]`, `[1]` and `[2,2,2]` all fall through to "no pivot, reverse everything"
and come back unchanged, which is the right answer for each.
""",
        ),
    ],
}


def next_permutation(nums: list[int]) -> list[int]:
    n = len(nums)

    # 1. Rightmost i with nums[i] < nums[i+1]. `>=` so plateaus are skipped.
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1

    if i >= 0:
        # 2. Rightmost value strictly greater than the pivot.
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]

    # 3. The suffix is non-increasing; reversing makes it the smallest tail.
    lo, hi = i + 1, n - 1
    while lo < hi:
        nums[lo], nums[hi] = nums[hi], nums[lo]
        lo += 1
        hi -= 1

    return nums


CASES = [
    (([1, 2, 3],), [1, 3, 2]),
    (([3, 2, 1],), [1, 2, 3]),  # already maximal: wraps round
    (([1, 1, 5],), [1, 5, 1]),
    (([1, 3, 2],), [2, 1, 3]),
    (([2, 3, 3, 1],), [3, 1, 2, 3]),  # plateau: a `>` pivot scan fails here
    (([5, 4, 7, 5, 3, 2],), [5, 5, 2, 3, 4, 7]),
    (([2, 2, 2],), [2, 2, 2]),
    (([1],), [1]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return next_permutation(list(nums))  # copy: the algorithm mutates in place
