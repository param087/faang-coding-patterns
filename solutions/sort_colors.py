"""Sort Colors — LeetCode 75."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Three regions, two boundaries, one scanner — and the scanner must not advance after a swap from the right.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Sort an array of 0s, 1s and 2s in place, in one pass, without a library sort.

Ask first: "can I do two passes?" Counting sort — tally the three values, then
overwrite — is trivial and correct. The interviewer will say one pass, which
is the actual question.
""",
        ),
        (
            "The insight",
            """
Maintain three regions with two boundaries and a scanner:

- everything left of `low` is 0
- everything right of `high` is 2
- `low..i` is 1
- `i..high` is unexamined

This is the **Dutch national flag** partition. Each step either places a value
or shrinks the unexamined region, so it terminates in one pass.
""",
        ),
        (
            "The detail that decides it",
            """
After swapping with `high`, **`i` does not advance.**

The value pulled in from the right has not been examined yet — it could be
anything. Advancing `i` skips it.

This is the bug, and it survives most inputs. `[2, 0, 1]` exposes it: with a
premature `i += 1` you get `[1, 0, 2]`, which is wrong. Run that case
explicitly rather than the sample.

By contrast, after swapping with `low` you *can* advance, because the value
coming from the left region is known to be a 1.
""",
        ),
        (
            "Follow-ups",
            """
- **k colours instead of 3.** The two-boundary trick does not generalise —
  this becomes counting sort. Knowing where a technique stops is worth as much
  as knowing where it works.
- **Sort an array of 0s and 1s** — a single write pointer, simpler still.
""",
        ),
    ],
}


def sort_colors(nums: list[int]) -> list[int]:
    low, i, high = 0, 0, len(nums) - 1

    while i <= high:
        if nums[i] == 0:
            nums[low], nums[i] = nums[i], nums[low]
            low += 1
            i += 1  # safe: the value from the left region is a known 1
        elif nums[i] == 2:
            nums[high], nums[i] = nums[i], nums[high]
            high -= 1  # i stays: the new nums[i] is unexamined
        else:
            i += 1

    return nums


CASES = [
    (([2, 0, 2, 1, 1, 0],), [0, 0, 1, 1, 2, 2]),
    (([2, 0, 1],), [0, 1, 2]),
    (([0],), [0]),
    (([2, 2, 2],), [2, 2, 2]),
    (([1, 0],), [0, 1]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return sort_colors(nums)
