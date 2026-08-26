"""Squares of a Sorted Array — LeetCode 977."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "The largest square is always at one end or the other, so fill the output from the back and never sort.",
    "time": "O(n)",
    "space": "O(n) output, O(1) extra",
    "sections": [
        (
            "What it asks",
            """
`nums` is sorted ascending and may contain negatives. Return the squares,
sorted ascending.

`sorted(x * x for x in nums)` is a one-liner and it is a fine thing to say out
loud — *then* say it is `O(n log n)` and that the input being sorted is there
for a reason. If you stop at the one-liner, you have answered a different
question than the one asked.
""",
        ),
        (
            "The insight",
            """
Squaring folds the array at zero: it is descending over the negatives and
ascending over the non-negatives — a **bitonic** sequence, minimum somewhere in
the middle, maxima at both ends.

So the largest remaining square is always at one of the two ends. Compare
`|nums[left]|` against `|nums[right]|`, take the larger, and write it into the
**last unfilled slot** of the output. n steps, no sort.

Note what this is *not*: it is not "find the zero-crossing by binary search,
then merge outwards". That also works and is also `O(n)`, but it needs a
correct binary search plus a merge with two exhaustion cases — three places to
get an off-by-one wrong instead of none.
""",
        ),
        (
            "The detail that decides it",
            """
**Fill back to front.** Writing forwards means you need the *smallest*
remaining square, which lives in the middle where you have no pointer. Every
attempt to build this front-to-front turns into the binary-search-and-merge
version.

Two more things that catch people:

- Compare **magnitudes**, not raw values. `nums[left] > nums[right]` is
  reversed for negatives; `abs()` (or comparing the squares directly) is what
  you want.
- The loop runs exactly `n` times and `left <= right` holds throughout, so
  neither index ever runs off the end and no extra guard is needed. On an empty
  array the loop body never executes — the `left = 0, right = -1` pair is never
  dereferenced.
- Ties (`abs(nums[left]) == abs(nums[right])`, e.g. `[-3, 3]`) can go either
  way; the `else` branch takes the right one and the counts still work out.
""",
        ),
    ],
}


def sorted_squares(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1

    for slot in range(n - 1, -1, -1):  # back to front: biggest square first
        if abs(nums[left]) > abs(nums[right]):
            result[slot] = nums[left] * nums[left]
            left += 1
        else:
            result[slot] = nums[right] * nums[right]
            right -= 1

    return result


CASES = [
    (([-4, -1, 0, 3, 10],), [0, 1, 9, 16, 100]),
    (([-7, -3, 2, 3, 11],), [4, 9, 9, 49, 121]),
    (([-3, -3, -2, 1],), [1, 4, 9, 9]),  # duplicates, and a tie in magnitude
    (([-3, -2, -1],), [1, 4, 9]),  # all negative: output order fully reverses
    (([1, 2, 3],), [1, 4, 9]),
    (([-5],), [25]),
    (([0],), [0]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return sorted_squares(nums)
