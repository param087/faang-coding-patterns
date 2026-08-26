"""Remove Duplicates from Sorted Array — LeetCode 26."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "A slow write pointer and a fast read pointer: the write pointer only advances when the value is new.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Collapse runs of equal values in a **sorted** array, in place, and return the
count `k` of distinct values. Only the first `k` slots are graded; whatever
sits beyond them is ignored.

Ask this before writing anything: **is the array sorted?** It is, and that is
the whole problem — duplicates are guaranteed adjacent, so "have I seen this
before?" collapses to "is it the same as the previous kept value?" and the set
you would otherwise need vanishes.
""",
        ),
        (
            "The insight",
            """
Two pointers moving the **same direction** at different speeds — the read/write
pair, which is a different animal from the converging pair in Two Sum II.

- `read` visits every element.
- `write` marks the end of the deduplicated prefix.

Copy `nums[read]` down to `nums[write]` only when it differs from
`nums[write - 1]`. Because `write <= read` always, you never overwrite a value
you have not read yet — that is the invariant that makes in-place safe.

Deleting in place with `list.pop()` instead would be O(n) per removal and
**O(n²)** overall: at n = 3·10⁴ with all-equal input that is ~9·10⁸ shifts.
""",
        ),
        (
            "Follow-ups",
            """
- **Allow at most two of each (LeetCode 80).** Compare against
  `nums[write - 2]` instead of `nums[write - 1]`, seeding `write = 2`. The same
  three lines.
- **At most `k` of each.** Compare against `nums[write - k]`, seed `write = k`.
  Being able to state that generalisation immediately is the point of the
  question; the base case is not.
- **Unsorted input.** The trick is gone — you are back to a hash set and O(n)
  space, or an O(n log n) sort first. Say which constraint you are trading.
""",
        ),
    ],
}


def remove_duplicates(nums: list[int]) -> int:
    if not nums:
        return 0

    write = 1  # nums[0] is always kept
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1

    return write


CASES = [
    (([1, 1, 2],), (2, [1, 2])),
    (([0, 0, 1, 1, 1, 2, 2, 3, 3, 4],), (5, [0, 1, 2, 3, 4])),
    (([],), (0, [])),
    (([1],), (1, [1])),
    (([1, 1, 1, 1],), (1, [1])),  # the O(n^2) pop() version dies here
    (([-3, -3, -1, 0, 0, 5],), (4, [-3, -1, 0, 5])),
    (([1, 2, 3],), (3, [1, 2, 3])),  # nothing to remove
]


def solve(nums: list[int]) -> tuple[int, list[int]]:
    scratch = list(nums)  # the algorithm mutates; keep CASES reusable
    k = remove_duplicates(scratch)
    return k, scratch[:k]
