"""Search in Rotated Sorted Array II — LeetCode 81."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "When both ends match the middle the which-half-is-sorted test is unanswerable; shed one from each end and accept an O(n) worst case.",
    "time": "O(log n) average, O(n) worst case",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Same as LeetCode 33 — a sorted array rotated at an unknown pivot — except
values may repeat, and you only return **whether** the target is present, not
where.

The change of return type is a hint. With duplicates there is no single "the
index" to return, and, more importantly, the log-time guarantee is gone. Say
that before you write anything; it is the graded observation.
""",
        ),
        (
            "The insight",
            """
In LeetCode 33 the test `nums[low] <= nums[mid]` decides which half is
properly sorted, and one comparison per step halves the array.

Duplicates break that test. Consider `[1, 1, 1, 0, 1]` and `[1, 0, 1, 1, 1]`:
in both, `nums[low]`, `nums[mid]` and `nums[high]` all read 1, and the two
arrays are **indistinguishable at those three positions** — yet the pivot is on
opposite sides. No comparison of three equal values can tell you which way to
go.

So handle that case separately and make no decision at all:

```
if nums[low] == nums[mid] == nums[high]:
    low += 1
    high -= 1
```

This is safe because `nums[low]` and `nums[high]` are duplicated at `mid`, so
discarding them cannot discard the only copy of the target. Whenever the three
are *not* all equal, the LeetCode 33 logic applies unchanged.
""",
        ),
        (
            "The complexity you must volunteer",
            """
`[1,1,1,...,1]` with the target absent shrinks by two per iteration: **O(n)**.
At n = 5000 that is 2500 iterations, and no clever tie-break fixes it — the
information simply is not there. Interviewers ask this question precisely to
see whether you notice that the guarantee is lost, so state it unprompted:
*O(log n) average, O(n) worst, and here is the adversarial input.*

Related traps:

- Only stripping one side (`low += 1`) is still correct, just slower to
  converge. Stripping both is the standard form.
- Do not "deduplicate first" — that is O(n) anyway and destroys the rotation
  structure you are searching.
- If the caller needs an **index** rather than a boolean, ask what to return
  for a value that appears many times. That question is why the problem was
  reduced to a boolean.
""",
        ),
    ],
}


def search(nums: list[int], target: int) -> bool:
    low, high = 0, len(nums) - 1

    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return True

        if nums[low] == nums[mid] == nums[high]:
            # Ambiguous: shed one duplicate from each end and retry.
            low += 1
            high -= 1
        elif nums[low] <= nums[mid]:  # left half is sorted
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:  # right half is sorted
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1

    return False


CASES = [
    (([2, 5, 6, 0, 0, 1, 2], 0), True),
    (([2, 5, 6, 0, 0, 1, 2], 3), False),
    (([1, 0, 1, 1, 1], 0), True),
    (([1, 1, 1, 0, 1], 0), True),
    (([1, 1, 1, 1, 1], 2), False),
    (([3, 1, 1], 3), True),
    (([1], 1), True),
    (([], 1), False),
]


def solve(nums: list[int], target: int) -> bool:
    return search(nums, target)
