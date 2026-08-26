"""Sort Array By Parity — LeetCode 905."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "This is a partition, not a sort — two pointers closing from the ends, and the only real question is whether stability matters.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Reorder the array so every even number precedes every odd one. **Any** such
arrangement is accepted.

That last sentence is the whole problem. Ask it explicitly — "does the relative
order within the evens need to be preserved?" — because the answer decides
which of two very different algorithms you write, and the interviewer is
waiting to see whether you notice.
""",
        ),
        (
            "The one-liner, and what it costs",
            """
`sorted(nums, key=lambda x: x % 2)` is correct, stable, and takes four
seconds. It is also O(n log n): at the constraint of n = 5000 that is roughly
5000 · 12 ≈ 61 000 comparisons against 5000 pointer steps, and at n = 10⁵ it
would be 1.7 × 10⁶ against 10⁵.

Nobody asks this question for the runtime at n = 5000. They ask it because the
one-pass answer is the **partition** step that Sort Colors, quickselect and
Move Zeroes are all built out of, and they want to see you write it cleanly.
""",
        ),
        (
            "The insight",
            """
Two pointers from the ends. Advance `left` while it points at an even number,
retreat `right` while it points at an odd number; when both are stuck, the left
one is odd and the right one is even, so a single swap fixes both and you move
both inwards.

Each index is visited once, every swap makes progress, so it is one pass, O(1)
extra space, and — importantly — **n/4 swaps on average** rather than the
n swaps a naive "collect evens then odds" copy performs.

The alternative one-pass shape is Lomuto's: a single `write` pointer, swapping
every even into place. Same complexity, more writes, and it is the version that
generalises to three-way partitioning.
""",
        ),
        (
            "The detail that decides it",
            """
**Neither one-pass version is stable.** Swapping from the ends scrambles the
relative order of both halves. If the follow-up is "keep the evens in their
original order", the two-pointer answer is simply wrong and you need either
`sorted(..., key=...)` (stable, O(n log n)) or an O(n) pass into a second array.
Naming this before being asked is the difference between a pass and a strong
pass.

**The portability trap:** `nums[i] % 2 == 1` is right in Python, where
`-3 % 2 == 1`, and **wrong** in C, C++, Java and Go, where `-3 % 2 == -1` and
the test silently fails for every negative odd number. Write `x % 2 != 0` or
`x & 1` if the code has to survive a language change. This input allows only
non-negative values, so the bug hides — until the follow-up removes that
constraint.
""",
        ),
        (
            "Dry run",
            """
`[3, 1, 2, 4]`

- `left = 0` sees 3 (odd, stuck), `right = 3` sees 4 (even, stuck) → swap →
  `[4, 1, 2, 3]`, pointers move to 1 and 2.
- `left = 1` sees 1 (odd, stuck), `right = 2` sees 2 (even, stuck) → swap →
  `[4, 2, 1, 3]`, pointers cross.

Result `[4, 2, 1, 3]`. Note that the evens came out `4, 2` — reversed from the
input. Perfectly valid here, and exactly what a stability follow-up would
reject.
""",
        ),
        (
            "Follow-ups",
            """
- **Sort Array By Parity II (922)** — evens must sit at even indices and odds
  at odd indices. Same two-pointer idea, but the pointers step by 2 down two
  separate tracks; a full sort no longer helps at all.
- **Sort Colors (75)** — three-way partition, `low/mid/high`. Once you have
  written this two-way version, that one is the same loop with an extra branch
  and the classic "do not advance `mid` after swapping with `high`" pitfall.
- **Move Zeroes (283)** — the same partition, but stability *is* required, so
  it must be the write-pointer form rather than the ends form.
""",
        ),
    ],
}


def sort_array_by_parity(nums: list[int]) -> list[int]:
    left, right = 0, len(nums) - 1

    while left < right:
        if nums[left] % 2 == 0:  # `% 2 != 0` if this must port to C/Java
            left += 1
        elif nums[right] % 2 == 1:
            right -= 1
        else:  # left is odd, right is even — one swap fixes both
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1

    return nums


CASES = [
    (([3, 1, 2, 4],), [4, 2, 1, 3]),
    (([1, 2, 3, 4],), [4, 2, 3, 1]),
    (([0, 1, 2],), [0, 2, 1]),
    (([-3, -2, 5, -4, 0],), [0, -2, -4, 5, -3]),
    (([1, 3, 5],), [1, 3, 5]),
    (([2, 4, 6],), [2, 4, 6]),
    (([0],), [0]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    # The partition is in place, so copy — CASES are reused across runs.
    return sort_array_by_parity(list(nums))
