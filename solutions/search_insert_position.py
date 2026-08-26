"""Search Insert Position — LeetCode 35."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "This is lower_bound: drop the equality branch and the surviving `low` is both the found index and the insertion point.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Sorted array of distinct integers. Return the index of `target`, or the index
where it would be inserted to keep the array sorted. O(log n).

The two outputs sound like two cases. They are one: **the index of the first
element that is not less than the target**. That is `lower_bound`, and it is
the single most reused shape in this pattern.
""",
        ),
        (
            "The insight",
            """
Take LeetCode 704 and delete the `return mid` branch:

```
if nums[mid] < target: low = mid + 1
else:                  high = mid
```

Now the loop never exits early, and it maintains one invariant: everything
left of `low` is `< target`, everything from `high` onward is `>= target`.
When `low == high` there is nothing in between, so `low` is the boundary — the
answer, whether or not the target is present.

Two consequences worth stating out loud:

- `high` starts at `len(nums)`, **not** `len(nums) - 1`. A target larger than
  everything must be allowed to land at index `n`.
- Nothing after the loop is needed. If you find yourself writing
  `if nums[low] == target` afterwards, you have written 704 by accident.

`bisect.bisect_left` is this function. Mention that you know it, then write
the loop — that is what is being tested.
""",
        ),
        (
            "Edge cases",
            """
- **Insert at the front**: `[1,3,5,6]`, target 0 → 0. The `else` branch keeps
  pulling `high` down to 0.
- **Insert past the end**: target 7 → **4**, which is out of bounds as an
  index. That is correct and is why `high = len(nums)`.
- **Empty array** → 0, with no special case.
- **Duplicates**: the problem promises distinct values, but the same loop
  returns the *leftmost* position on a tie. Swapping `<` for `<=` gives
  `upper_bound`, the rightmost. Knowing which one you wrote is the whole of
  LeetCode 34.
""",
        ),
    ],
}


def search_insert(nums: list[int], target: int) -> int:
    low, high = 0, len(nums)  # high = n: the target may belong past the end

    while low < high:
        mid = (low + high) // 2
        if nums[mid] < target:
            low = mid + 1
        else:
            high = mid

    return low  # first index with nums[i] >= target


CASES = [
    (([1, 3, 5, 6], 5), 2),
    (([1, 3, 5, 6], 2), 1),
    (([1, 3, 5, 6], 7), 4),
    (([1, 3, 5, 6], 0), 0),
    (([-5, -2, 0], -3), 1),
    (([1], 1), 0),
    (([1], 0), 0),
    (([], 4), 0),
]


def solve(nums: list[int], target: int) -> int:
    return search_insert(nums, target)
