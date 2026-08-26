"""Find Peak Element — LeetCode 162."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "Unsorted, yet binary-searchable: an uphill step guarantees a peak on that side, because the array ends in virtual −infinity.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return the index of *any* element strictly greater than both neighbours.
Out-of-bounds neighbours count as −∞. Adjacent elements are guaranteed
unequal. O(log n) is required, which is the surprise: the array is **not
sorted**.

Ask what "any peak" means for grading — the judge accepts any valid index, so
your loop does not have to find a particular one. That freedom is what makes
throwing away half the array legal.
""",
        ),
        (
            "The insight",
            """
Binary search does not need sortedness. It needs a test at `mid` that rules
out one side, and here is one:

> If `nums[mid] < nums[mid + 1]`, a peak **must** exist strictly to the right.

Why must it? Start climbing from `mid + 1`. Either you keep going up and run
off the end — but the element past the end is −∞, so the last element is a
peak — or you stop climbing somewhere, and the element where you stop is a
peak. The ascent cannot escape; it must terminate in one. So `low = mid + 1`
throws away the left half and keeps a guaranteed answer.

Symmetrically, `nums[mid] > nums[mid + 1]` means `mid` itself is either a peak
or has a peak to its left, so `high = mid` — keeping `mid`, since it is a
candidate.

Two elements, one comparison, no equality case (adjacent values differ). Loop
`while low < high` and return `low`.
""",
        ),
        (
            "The boundary convention, and the wrong first answer",
            """
The wrong first answer is "scan for the maximum" — O(n), correct but not what
was asked — or a three-way comparison `nums[mid-1] < nums[mid] > nums[mid+1]`
with index guards at both ends. The guards are what break it: at `mid = 0`
there is no `mid - 1`, and people write `mid > 0 and ...` in a way that makes a
descending array return nothing.

The one-sided test avoids all of it. `mid` is `(low + high) // 2` with
`low < high`, so `mid < high <= n - 1` and `mid + 1` is **always** in range.
No guard is ever needed.

Sanity checks the convention buys you: a strictly ascending array peaks at the
last index, a strictly descending one at index 0, and a single element is a
peak with both neighbours at −∞.
""",
        ),
    ],
}


def find_peak_element(nums: list[int]) -> int:
    low, high = 0, len(nums) - 1

    while low < high:
        mid = (low + high) // 2  # mid < high, so mid + 1 is always in range
        if nums[mid] < nums[mid + 1]:
            low = mid + 1  # climbing: a peak is guaranteed to the right
        else:
            high = mid  # mid is a candidate — keep it

    return low


CASES = [
    (([1, 2, 3, 1],), 2),
    (([1, 2, 1, 3, 5, 6, 4],), 5),  # index 1 is also valid; this loop finds 5
    (([1, 3, 2, 1],), 1),
    (([1],), 0),
    (([1, 2],), 1),
    (([2, 1],), 0),
    (([1, 2, 3, 4, 5],), 4),
    (([5, 4, 3, 2, 1],), 0),
]


def solve(nums: list[int]) -> int:
    return find_peak_element(nums)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # The judge accepts any peak, so verify the property rather than the index.
    extra = [
        [1, 2, 1, 3, 5, 6, 4],
        [6, 5, 4, 3, 2, 1, 7],
        [1, 4, 3, 6, 2, 7, 1],
        [10, 20],
        [3],
    ]
    for nums in extra:
        i = solve(nums)
        left = nums[i - 1] if i > 0 else float("-inf")
        right = nums[i + 1] if i + 1 < len(nums) else float("-inf")
        assert left < nums[i] > right, (nums, i)
