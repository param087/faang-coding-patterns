"""Pancake Sorting — LeetCode 969."""

from __future__ import annotations

META = {
    "pattern": "sorting",
    "insight": "Two flips place any element: rotate the largest unplaced value to the front, then flip it to the back — selection sort in flips.",
    "time": "O(n²)",
    "space": "O(n) — the flip list is the output",
    "sections": [
        (
            "What it asks",
            """
The only move you have is "reverse the first `k` pancakes". Return the
*sequence of `k` values* that leaves the array sorted ascending. The array is a
permutation of `1..n`, and the answer is a list of lengths, not the array.

Two clarifying questions, and the second one is the whole interview:

- **Is `k` a length or an index?** A length, 1-based, `1 <= k <= n`. Emitting
  indices is the single most common way to fail this.
- **Does the sequence have to be the shortest one?** No — LeetCode accepts
  anything within `10 * n` flips. Say this out loud, because *minimising* flips
  is a different problem: computing the pancake number of a given permutation is
  NP-hard, so an interviewer asking for the minimum has left coding-round
  territory.
""",
        ),
        (
            "The insight",
            """
Once you accept that the flip count only has to be *linear*, not minimal, this
collapses into selection sort where each placement costs two moves instead of
one swap.

To park the largest unplaced value at index `size - 1`:

1. flip its prefix so it lands at the front (`flip(i + 1)`);
2. flip the whole unplaced prefix so the front travels to the back
   (`flip(size)`).

Everything to the right of `size - 1` is already sorted and never moves again,
so shrink `size` and repeat. The reversal in step 2 scrambles the order of the
remaining elements, and that is fine — the loop makes no assumption about them
beyond "the maximum is somewhere in `arr[:size]`".

Locating that maximum is the O(n) part of each round, hence O(n²) overall.
With `n <= 100` on this problem that is 10⁴ operations; nobody is asking you to
beat it.
""",
        ),
        (
            "The flip budget, and the two flips you must not emit",
            """
Two flips per element gives `2(n - 1)`, and the last round (`size == 2`) needs
at most one, so the bound is **2n - 3** against an allowance of `10n`. Comfort-
able — which is exactly why the greedy is acceptable.

Two skips are worth writing deliberately:

- **The value is already at `size - 1`.** `continue`. Flipping anyway is still
  *accepted*, but a reviewer reads an unconditional two-flip loop as "did not
  notice".
- **The value is already at index 0.** Then `flip(i + 1)` is `flip(1)`, a no-op
  that burns a flip. Only emit the second flip.

A sorted input must therefore produce `[]`, and `[5, 4, 3, 2, 1]` must produce
a single flip of the whole array — both are in the cases below, and a solution
that emits `2n` flips for either is doing something it should not.

Verification matters more here than usual: because any valid answer passes, a
test that only compares against one expected list is testing your
implementation, not the problem. Apply the flips and assert the array comes out
sorted and that every `k` is in range.
""",
        ),
    ],
}


def pancake_sort(arr: list[int]) -> list[int]:
    stack = list(arr)  # the caller's array is not ours to scramble
    flips: list[int] = []

    for size in range(len(stack), 1, -1):
        largest = max(range(size), key=stack.__getitem__)

        if largest == size - 1:
            continue  # already parked

        if largest > 0:  # skip the no-op flip(1)
            flips.append(largest + 1)  # a length, not an index
            stack[: largest + 1] = reversed(stack[: largest + 1])

        flips.append(size)
        stack[:size] = reversed(stack[:size])

    return flips


def apply_flips(arr: list[int], flips: list[int]) -> list[int]:
    stack = list(arr)
    for k in flips:
        stack[:k] = reversed(stack[:k])
    return stack


CASES = [
    # (flips this implementation emits, the array after applying them)
    (([3, 2, 4, 1],), ([3, 4, 2, 3, 2], [1, 2, 3, 4])),
    (([1, 2, 3],), ([], [1, 2, 3])),  # already sorted -> no flips at all
    (([5, 4, 3, 2, 1],), ([5], [1, 2, 3, 4, 5])),  # reversed -> exactly one flip
    (([2, 1],), ([2], [1, 2])),
    (([1, 3, 2],), ([2, 3, 2], [1, 2, 3])),
    (([1, 5, 4, 3, 2],), ([2, 5, 3, 4], [1, 2, 3, 4, 5])),
    (([1],), ([], [1])),
    (([],), ([], [])),
]


def solve(arr: list[int]) -> tuple[list[int], list[int]]:
    flips = pancake_sort(arr)
    return flips, apply_flips(arr, flips)


def check() -> None:
    for args, expected in CASES:
        assert solve(*args) == expected, args

    # Any valid flip sequence is accepted, so check the properties, not the list.
    permutations = [
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [3, 1, 4, 5, 2],
        [2, 4, 1, 5, 3],
        [4, 4, 4, 4],  # duplicates: the greedy never needs uniqueness
        [7, 3, 9, 1, 8, 2, 6, 5, 4],
    ]
    for arr in permutations:
        flips = pancake_sort(arr)
        assert all(1 <= k <= len(arr) for k in flips), (arr, flips)
        assert len(flips) <= 10 * len(arr), (arr, flips)
        assert len(flips) <= max(0, 2 * len(arr) - 3), (arr, flips)
        assert apply_flips(arr, flips) == sorted(arr), (arr, flips)

    # solve() must not disturb the caller's array.
    original = [3, 1, 2]
    solve(original)
    assert original == [3, 1, 2]
