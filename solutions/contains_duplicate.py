"""Contains Duplicate — LeetCode 217."""

from __future__ import annotations

META = {
    "pattern": "arrays-hashing",
    "insight": "The question is not which value repeats, only whether any does, so a set membership test replaces the pairwise scan.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Return `True` if any value appears at least twice, `False` if every element is
distinct.

The one clarifying question worth asking: **may I mutate the input?** If yes,
sorting gives O(n log n) time and O(1) extra space, which is the right answer
when memory is the constraint rather than time. If no, the set is the answer.
Also confirm n — LeetCode says 10⁵, so O(n²) is 10¹⁰ operations and dead on
arrival.
""",
        ),
        (
            "The insight",
            """
Trading memory for time is the entire pattern. A set answers "have I seen this
before?" in O(1), so a single pass decides it.

Two ways to write it, and the difference matters:

```python
len(set(nums)) != len(nums)     # always builds the whole set
```

versus the explicit loop, which **returns on the first repeat**. On
`[1, 1, 1, ..., 1]` with 10⁵ elements the one-liner still allocates a set and
walks the whole array; the loop stops at index 1. Same asymptotics, very
different behaviour on adversarial input — say this out loud and then write
whichever you like.
""",
        ),
        (
            "Follow-ups",
            """
- **Contains Duplicate II** — duplicates within `k` indices of each other. Same
  set, but slide a window: drop `nums[i - k - 1]` as you advance, so the set
  only ever holds the last `k` values.
- **Contains Duplicate III** — values within `t` of each other *and* indices
  within `k`. Now a plain set fails; you need buckets of width `t + 1` (or a
  sorted container), because you are asking a range question, not an equality
  question.
- **"The array does not fit in memory."** Sort externally, or filter with a
  Bloom filter first and verify the candidates. A Bloom filter gives false
  positives but never false negatives, which is exactly the right asymmetry.
""",
        ),
    ],
}


def contains_duplicate(nums: list[int]) -> bool:
    seen: set[int] = set()

    for value in nums:
        if value in seen:
            return True  # early exit; `len(set(nums)) != len(nums)` cannot do this
        seen.add(value)

    return False


CASES = [
    (([1, 2, 3, 1],), True),
    (([1, 2, 3, 4],), False),
    (([1, 1, 1, 3, 3, 4, 3, 2, 4, 2],), True),
    (([1, 2, 3, 4, 5, 1],), True),  # duplicates at the ends: an adjacent-pair check misses this
    (([-2, -1, 0, 1, 2],), False),
    (([-1, -1],), True),
    (([7],), False),
    (([],), False),
]


def solve(nums: list[int]) -> bool:
    return contains_duplicate(nums)
