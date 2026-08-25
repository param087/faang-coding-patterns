"""Longest Consecutive Sequence — LeetCode 128."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "Only start counting from a value with no left neighbour, and every run is walked exactly once.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given an unsorted array, return the length of the longest run of consecutive
integers. The runs need not be contiguous in the array.

Ask: duplicates allowed (yes, and they should not extend a run), negatives
(yes), is O(n) required (yes — that is the whole question).
""",
        ),
        (
            "The obvious answer, and why it is not enough",
            """
Sort, then scan for runs. O(n log n), correct, and easy.

The interviewer will ask you to beat it. The sentence that gets you there:
**"the sort is doing more work than the question needs — it gives me total
order when I only need adjacency."** Say that before writing anything.
""",
        ),
        (
            "The insight",
            """
Put everything in a set, then walk each run — but **only start a walk from a
value that has no left neighbour**. That single `continue` is what makes it
linear.

Without it, you would walk every run from every one of its members, and the
whole thing is quadratic. With it, each run is traversed exactly once across
the entire loop, so the inner `while` costs O(n) *in total* rather than per
element.

This is the same amortised argument as the monotonic stack: an inner loop is
not automatically a multiplier on the outer one.
""",
        ),
        (
            "Dry run",
            """
`[100, 4, 200, 1, 3, 2]`

- 100 has no 99 → starts a run of length 1.
- 4 **is skipped** — 3 exists, so someone else will count this run.
- 200 runs alone.
- 1 has no 0 → walks 1, 2, 3, 4 → length 4.

The skipped values are the point. Trace one to prove the inner loop does not
re-walk them.
""",
        ),
    ],
}


def longest_consecutive(nums: list[int]) -> int:
    pool = set(nums)  # dedupes, and gives O(1) membership
    best = 0

    for value in pool:
        if value - 1 in pool:
            continue  # not the start of a run; someone else counts it

        length = 1
        while value + length in pool:
            length += 1
        best = max(best, length)

    return best


CASES = [
    (([100, 4, 200, 1, 3, 2],), 4),
    (([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), 9),
    (([1, 2, 0, 1],), 3),
    (([5],), 1),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return longest_consecutive(nums)
