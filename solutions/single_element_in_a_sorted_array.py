"""Single Element in a Sorted Array — LeetCode 540."""

from __future__ import annotations

META = {
    "pattern": "binary-search",
    "insight": "Before the lone element every pair starts at an even index; after it every pair starts at an odd one — binary search the break.",
    "time": "O(log n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
A sorted array where every value appears exactly twice except one, which
appears once. Return that value in **O(log n) time and O(1) space** — the
complexity bound is the problem; without it this is a one-line XOR.

Worth confirming: the array is sorted, so duplicates are **adjacent** (this is
the fact the whole solution rests on), and the length is therefore always odd.
""",
        ),
        (
            "The insight",
            """
XOR over the whole array is the answer everyone reaches for, and it is right —
but it is O(n), and reading all n elements is precisely what the bound forbids.
Same for scanning pairs two at a time. Neither uses the sort.

Use it like this. Pair up the array from the left and look at the **index each
pair starts on**:

```
[1, 1, 2, 3, 3, 4, 4, 8, 8]
 0  1     3  4  5  6  7  8      pairs at 0, then 3, 5, 7
       ^ the single element at index 2 shifts everything after it
```

Before the single element, every pair sits at `(even, odd)`. After it, the
parity flips to `(odd, even)`. So for any **even** index `i`:

- `nums[i] == nums[i + 1]` → the pairing is still intact here, the odd one out
  is strictly to the right;
- otherwise it is at `i` or to the left.

That is a monotone predicate over the array, which is all binary search needs.
No arithmetic on values at all — this works identically for negatives.
""",
        ),
        (
            "Forcing `mid` even",
            """
`mid = (low + high) // 2` lands on an odd index half the time, and on an odd
index the whole parity argument inverts: you would be comparing the *second*
half of a pair with the *first* half of the next one and reading the answer
backwards.

`mid -= mid & 1` snaps it down to the even index below. That is the line the
solution lives or dies on, and it is the one to point at when asked to explain
the code.

Two consequences worth stating:

- Because `mid` is even and `mid < high`, `mid + 1` is always in bounds — no
  guard needed.
- The advance is `low = mid + 2`, not `mid + 1`: you have just verified a whole
  pair, so skip both. `mid + 1` still terminates but can leave `low` odd and
  costs you the invariant.

The loop is `while low < high` with `high = mid`, and it exits with
`low == high` pointing at the answer. There is no empty case to defend against
— an array of odd length ≥ 1 always has exactly one such element.
""",
        ),
    ],
}


def single_non_duplicate(nums: list[int]) -> int:
    low, high = 0, len(nums) - 1

    while low < high:
        mid = (low + high) // 2
        mid -= mid & 1  # snap down to an even index: pairs start on even ones

        if nums[mid] == nums[mid + 1]:
            low = mid + 2  # pairing intact through mid+1, answer is to the right
        else:
            high = mid  # the break is at mid or earlier

    return nums[low]


CASES = [
    (([1, 1, 2, 3, 3, 4, 4, 8, 8],), 2),
    (([3, 3, 7, 7, 10, 11, 11],), 10),
    (([1],), 1),  # single element is the whole array
    (([1, 1, 2],), 2),  # answer at the far right
    (([2, 3, 3],), 2),  # answer at the far left
    (([-5, -5, -3, -1, -1],), -3),  # negatives: no arithmetic on values
    (([0, 0, 1, 1, 2, 2, 3],), 3),
    (([1, 1, 2, 2, 3, 3, 4, 4, 5],), 5),
]


def solve(nums: list[int]) -> int:
    return single_non_duplicate(nums)
