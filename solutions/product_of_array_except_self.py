"""Product of Array Except Self — LeetCode 238."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "The answer at i is everything to its left times everything to its right — two sweeps, no division.",
    "time": "O(n)",
    "space": "O(1) extra, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Return an array where `answer[i]` is the product of every element **except**
`nums[i]`. You may not use division, and it must run in O(n).

Ask: can the array contain zeros (yes — and that is exactly why division is
banned), can it contain negatives (yes), is the output array counted against
the space bound (usually not, and that is what makes O(1) achievable).
""",
        ),
        (
            "Why division is forbidden",
            """
The tempting solution is `total // nums[i]`. It breaks on zeros: one zero
makes every other answer zero and its own answer the product of the rest; two
zeros make everything zero. Handling that needs a zero count and special
cases, and the constraint rules it out anyway.

Say this — knowing *why* the restriction exists is better than just obeying it.
""",
        ),
        (
            "The insight",
            """
`answer[i]` is (everything to the left of i) × (everything to the right of i).

Sweep left to right accumulating the running prefix product into the output.
Then sweep right to left multiplying by a running suffix product held in a
single variable. Two passes, no extra array.

The prefix starts at 1 and the suffix starts at 1, because the product of
nothing is 1 — that identity is what removes the boundary special cases.
""",
        ),
        (
            "Dry run",
            """
`[1, 2, 3, 4]`

After the left pass, `answer` holds the prefix products:
`[1, 1, 2, 6]`.

Right pass with `suffix` starting at 1:
- i=3: `6 * 1 = 6`, suffix becomes 4
- i=2: `2 * 4 = 8`, suffix becomes 12
- i=1: `1 * 12 = 12`, suffix becomes 24
- i=0: `1 * 24 = 24`

Result `[24, 12, 8, 6]`.
""",
        ),
    ],
}


def product_except_self(nums: list[int]) -> list[int]:
    n = len(nums)
    answer = [1] * n

    prefix = 1
    for i in range(n):
        answer[i] = prefix  # everything strictly left of i
        prefix *= nums[i]

    suffix = 1
    for i in range(n - 1, -1, -1):
        answer[i] *= suffix  # times everything strictly right of i
        suffix *= nums[i]

    return answer


CASES = [
    (([1, 2, 3, 4],), [24, 12, 8, 6]),
    (([-1, 1, 0, -3, 3],), [0, 0, 9, 0, 0]),
    (([0, 0],), [0, 0]),
    (([2, 3],), [3, 2]),
    (([5],), [1]),
    (([],), []),
]


def solve(nums: list[int]) -> list[int]:
    return product_except_self(nums)
