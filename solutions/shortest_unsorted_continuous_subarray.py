"""Shortest Unsorted Continuous Subarray — LeetCode 581."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "The right edge is the last element below the running prefix max; the left edge is the first element above the running suffix min.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Find the shortest contiguous window such that sorting **only that window**
leaves the whole array sorted ascending. Return its length, `0` if the array is
already sorted.

Ask whether the order is non-decreasing (duplicates allowed) — it is, and that
single word decides whether your comparisons are `<` or `<=`. Getting it wrong
still passes the textbook examples and fails on `[1, 2, 2, 3]`.

Sorting a copy and comparing element-wise to find the first and last mismatch
is a legitimate `O(n log n)` answer and takes 30 seconds to write. Offer it,
then give the linear one — the whole point of the question is the `O(n)`,
`O(1)` version.
""",
        ),
        (
            "The insight",
            """
Two sweeps, each carrying one number.

**Left to right**, track the running maximum of the prefix. Any element smaller
than everything before it is out of place, and the **last** such index is the
right edge — every element after it is at least the max of everything before,
so it is already in its final position.

**Right to left**, track the running minimum of the suffix. Any element larger
than something after it is out of place, and the **first** such index is the
left edge.

If the forward sweep never fires, the array is sorted: return `0`.

Two pointers converging from the ends of the array, each defined by a
monotone quantity carried in from its own side. That symmetry is the answer.
""",
        ),
        (
            "The boundary everyone gets wrong",
            """
The instinct is to scan for the first adjacent inversion `nums[i] > nums[i+1]`
and call that the left edge. It is not.

`[1, 3, 2, 0, 5]` — the first inversion is at index 1 (`3 > 2`), but the
answer's left edge is index **0**: the `0` at index 3 must end up before the
`1`, so the `1` is inside the window too. Correct answer **4**
(`[1, 3, 2, 0]`), not 3. The suffix-minimum sweep catches it because it
compares each element against everything to its right, not just its neighbour.

The other trap is duplicates. Both comparisons must be **strict**:
`nums[i] < running_max` and `nums[i] > running_min`. Use `<=` and `[1, 2, 2, 3]`
reports a window of length 2 instead of 0.

Follow-up worth having ready: "return the sorted array" is *not* free from
this — you still have to sort the window, `O(k log k)`. And the two-sweep
result is exactly the same window the sort-a-copy method finds, which is a
cheap way to sanity-check your implementation against a brute force.
""",
        ),
    ],
}


def find_unsorted_subarray(nums: list[int]) -> int:
    n = len(nums)

    # Right edge: last index that falls below the max of everything before it.
    end = -1
    running_max = float("-inf")
    for i in range(n):
        if nums[i] < running_max:
            end = i
        else:
            running_max = nums[i]

    if end == -1:  # never fired -> already sorted
        return 0

    # Left edge: first index that rises above the min of everything after it.
    start = n
    running_min = float("inf")
    for i in range(n - 1, -1, -1):
        if nums[i] > running_min:
            start = i
        else:
            running_min = nums[i]

    return end - start + 1


CASES = [
    (([2, 6, 4, 8, 10, 9, 15],), 5),
    (([1, 3, 2, 0, 5],), 4),  # first adjacent inversion is NOT the left edge
    (([1, 2, 2, 3],), 0),  # strict comparisons, or this returns 2
    (([1, 3, 2, 2, 2],), 4),
    (([2, 1],), 2),
    (([1, 2, 3, 4],), 0),
    (([1],), 0),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return find_unsorted_subarray(nums)
