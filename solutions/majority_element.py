"""Majority Element — LeetCode 169."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "Cancel each pair of differing votes; an element holding more than half the array cannot be cancelled away.",
    "time": "O(n)",
    "space": "O(1)",
    "sections": [
        (
            "What it asks",
            """
Return the element that appears **more than** `⌊n/2⌋` times. LeetCode
guarantees such an element exists — pin that down before you write anything,
because the guarantee is the difference between a one-pass answer and a
two-pass one.

Also pin down *strictly* more than half. At `n = 4`, three copies qualify and
two do not, and the tie case is where an "at least" reading silently breaks.

The follow-up is printed on the problem: **O(n) time, O(1) space.** A `Counter`
is the obvious O(n)/O(n) answer and worth stating in one breath before moving
past it.
""",
        ),
        (
            "The insight",
            """
Boyer–Moore voting. Picture every element as a vote and repeatedly delete a
pair of *differing* votes. Each deletion removes at most one copy of the
majority element and at least one non-majority element, so if one value started
with more than half the total, it still holds more than half of what remains —
and it is whatever survives to the end.

The implementation is that argument with a counter:

- `count == 0` means everything so far has cancelled out. Adopt the current
  element as the new candidate.
- Matching the candidate reinforces it; differing from it cancels one copy.

Two lines of state, one pass, O(1) space.

What the counter is **not**: it is not the frequency of the candidate. On
`[2, 2, 1, 1, 1, 2, 2]` it ends at 1, not 4. Anyone who reads it as a frequency
will build the wrong follow-up.
""",
        ),
        (
            "The guarantee is load-bearing",
            """
Drop the "a majority exists" promise and this algorithm returns nonsense
rather than an error: on `[1, 2, 3]` it returns `3`, which is simply the last
element it happened to adopt. Boyer–Moore finds *the only possible candidate*,
not a verified answer.

So whenever the guarantee is not given — and interviewers remove it on purpose
— add a **second pass** that counts the candidate and confirms it exceeds
`n // 2`. Still O(n) time, still O(1) space, and volunteering it before being
asked is the whole signal here.

The generalisation, **Majority Element II (229)**, asks for everything above
`⌊n/3⌋`. There can be at most two such values, so run two candidates with two
counters, then verify both — because at `n/3` the verification pass is
mandatory: the answer set may be empty.
""",
        ),
    ],
}


def majority_element(nums: list[int]) -> int | None:
    candidate: int | None = None
    count = 0

    for value in nums:
        if count == 0:
            candidate = value  # everything so far cancelled out
        count += 1 if value == candidate else -1

    return candidate  # correct only because a majority is guaranteed to exist


CASES = [
    (([3, 2, 3],), 3),
    (([2, 2, 1, 1, 1, 2, 2],), 2),
    (([4, 4, 1, 4, 1, 1, 1],), 1),  # the candidate only flips on the final element
    (([1, 2, 3, 3, 3, 3, 3],), 3),  # a late run overtakes an early candidate
    (([-1, -1, -1, 2, 3],), -1),
    (([6, 5, 5],), 5),
    (([1],), 1),
    (([],), None),
]


def solve(nums: list[int]) -> int | None:
    return majority_element(nums)
