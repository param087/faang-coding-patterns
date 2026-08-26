"""Sort an Array — LeetCode 912."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "Write merge sort: quicksort with a fixed pivot is quadratic on exactly the adversarial inputs the graders feed it.",
    "time": "O(n log n) worst case",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Sort an integer array without calling the language's built-in sort, in
O(n log n) time and with as little extra space as you can manage.

It is the one problem where "I would call `sorted`" is the wrong answer, so
treat it as a request to demonstrate an algorithm end to end. Ask for the
constraints — here `n ≤ 5·10⁴` and `-5·10⁴ ≤ nums[i] ≤ 5·10⁴` — because that
second bound is doing more work than it looks.
""",
        ),
        (
            "The insight",
            """
Merge sort is the answer to give under time pressure:

- **Guaranteed** O(n log n), not average-case. No pivot to get wrong.
- Stable, which matters the moment the elements stop being bare integers.
- The merge is the reusable part — Merge k Sorted Lists, Count of Smaller
  Numbers After Self and counting inversions are all this function with a
  counter bolted on.

Split at the midpoint, sort both halves, then walk the two sorted halves with
two indices taking the smaller head each time. Using `<=` rather than `<` in
that comparison is what makes it stable. Recursion depth is log₂(5·10⁴) ≈ 16,
comfortably inside Python's limit.

The cost is O(n) auxiliary space. Heapsort trades that away — O(1) extra, still
guaranteed O(n log n) — but is not stable and does far worse on cache locality.
Say which trade-off you picked and why.
""",
        ),
        (
            "The test case that kills quicksort",
            """
Naive quicksort — pivot on the first or last element — is O(n²) on an
already-sorted array. At n = 5·10⁴ that is 2.5 × 10⁹ comparisons, which is a
timeout, and LeetCode's test set for this problem contains exactly such inputs
plus a large all-equal array. This is the single most common way to fail a
question you have "already solved".

If you want to write quicksort anyway, you need **both** fixes:

- a **randomised** (or median-of-three) pivot, which handles sorted input;
- a **three-way** partition into `< pivot`, `== pivot`, `> pivot`, which handles
  the all-equal array that a two-way partition degrades to O(n²) on.

And the extra follow-up worth naming: with values bounded by ±5·10⁴, a counting
sort finishes in O(n + 10⁵) with no comparisons at all — beating O(n log n) by
using the constraint the problem statement handed you.
""",
        ),
    ],
}


def _merge(left: list[int], right: list[int]) -> list[int]:
    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # `<=`, not `<` — this is what makes it stable
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def sort_array(nums: list[int]) -> list[int]:
    if len(nums) <= 1:
        return list(nums)
    mid = len(nums) // 2
    return _merge(sort_array(nums[:mid]), sort_array(nums[mid:]))


CASES = [
    (([5, 2, 3, 1],), [1, 2, 3, 5]),
    (([5, 1, 1, 2, 0, 0],), [0, 0, 1, 1, 2, 5]),
    (([1, 2, 3, 4, 5, 6, 7, 8],), [1, 2, 3, 4, 5, 6, 7, 8]),
    (([8, 7, 6, 5, 4, 3, 2, 1],), [1, 2, 3, 4, 5, 6, 7, 8]),
    (([2, 2, 2, 2, 2],), [2, 2, 2, 2, 2]),
    (([-4, 0, 7, 4, 9, -5, -1, 0, -7, -1],), [-7, -5, -4, -1, -1, 0, 0, 4, 7, 9]),
    (([1],), [1]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return sort_array(nums)
