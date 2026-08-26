"""Merge Sorted Array — LeetCode 88."""

from __future__ import annotations

META = {
    "pattern": "two-pointers",
    "insight": "Merge from the back: the tail of nums1 is scratch space, so every write lands on a slot already consumed.",
    "time": "O(m + n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
`nums1` has `m` real values followed by `n` zero placeholders; `nums2` has `n`
values. Both are sorted ascending. Merge `nums2` into `nums1` **in place**.

Confirm the padding: `len(nums1) == m + n` exactly. That fact — the destination
is already the right size — is what makes O(1) space possible, and it is the
detail candidates read past.
""",
        ),
        (
            "The insight",
            """
Merging front-to-back is the reflex, and it is wrong here: writing a value from
`nums2` into `nums1[0]` destroys a value you still need, so you end up shifting
the rest right, and the merge becomes **O(m·n)**.

Go backwards instead. Fill from index `m + n - 1` down, always taking the
larger of the two current tails. The write pointer starts past all the live
data and the read pointer `i` starts at `m - 1`, so **`write >= i` always** —
every slot you write has already been consumed. The placeholders are not
padding to be worked around; they are exactly the scratch space you need.
""",
        ),
        (
            "The detail that decides it",
            """
When the loop ends, one input is exhausted. **Only `nums2`'s leftovers need
copying.**

If `nums1` runs out first, its remaining `nums2` values are the smallest, and
they belong at the front — hence the trailing `while j >= 0` loop. If `nums2`
runs out first, `nums1`'s remaining values are *already sitting in the right
slots*, untouched, because the write pointer never passed them. Copying them
would be a no-op; forgetting the *other* loop silently leaves zeros behind.

Test both directions explicitly:

- `[4,5,6,0,0,0], m=3, [1,2,3], n=3` → `[1,2,3,4,5,6]`. `nums1` empties first,
  so the `j` loop does all the work. Skip that loop and you get
  `[0,0,0,4,5,6]`.
- `[1,2,3,0,0,0], m=3, [4,5,6], n=3` → `[1,2,3,4,5,6]`. `nums2` empties first
  and the answer is already correct with no extra loop.

Also handle `m = 0` (`nums1 == [0]`, `nums2 == [1]`) and `n = 0`
(`nums2 == []`); both fall out of the same code with no special case.
""",
        ),
    ],
}


def merge(nums1: list[int], m: int, nums2: list[int], n: int) -> list[int]:
    i, j = m - 1, n - 1
    write = m + n - 1

    while i >= 0 and j >= 0:
        if nums1[i] > nums2[j]:
            nums1[write] = nums1[i]
            i -= 1
        else:
            nums1[write] = nums2[j]
            j -= 1
        write -= 1

    while j >= 0:  # nums1 emptied first; nums1's own leftovers are already in place
        nums1[write] = nums2[j]
        j -= 1
        write -= 1

    return nums1


CASES = [
    (([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3), [1, 2, 2, 3, 5, 6]),
    (([4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3), [1, 2, 3, 4, 5, 6]),  # needs the j loop
    (([1, 2, 3, 0, 0, 0], 3, [4, 5, 6], 3), [1, 2, 3, 4, 5, 6]),  # never needs it
    (([1], 1, [], 0), [1]),
    (([0], 0, [1], 1), [1]),
    (([2, 0], 1, [1], 1), [1, 2]),
    (([-1, 3, 0, 0], 2, [-2, 1], 2), [-2, -1, 1, 3]),
]


def solve(nums1: list[int], m: int, nums2: list[int], n: int) -> list[int]:
    return merge(list(nums1), m, nums2, n)  # copy: merge writes into nums1
