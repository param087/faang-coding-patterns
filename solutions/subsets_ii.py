"""Subsets II — LeetCode 90."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Sort so equal values are adjacent, then at each depth allow only the first of a run of equals to start a branch.",
    "time": "O(n · 2ⁿ)",
    "space": "O(n) for the recursion, excluding the output",
    "sections": [
        (
            "What it asks",
            """
The power set of a multiset: every subset of `nums`, with **no duplicate
subsets** in the output. Order is free.

Ask whether the input is sorted. If it is, you skip the sort and the answer is
O(n · 2ⁿ) rather than O(n log n + n · 2ⁿ) — a detail nobody volunteers.

Also worth pinning down: duplicates are duplicates *by value*, so `[1,2]` and
`[2,1]` are the same subset. That is what forces a canonical order, and
sorting gives you one for free.
""",
        ),
        (
            "The insight",
            """
The naive fix — collect everything with the plain Subsets recursion, then
dedup via `set(map(tuple, ...))` — works and is O(n · 2ⁿ) all the same, but it
builds `2ⁿ` subsets to keep possibly far fewer. With `[1,1,1,…]` twenty deep
that is a million lists to produce 21 answers.

Prune instead. **Sort** so equal values sit next to each other, then inside the
loop at each depth, skip any candidate equal to the one just tried at that same
depth:

```python
if i > start and nums[i] == nums[i - 1]:
    continue
```

Reading it as a rule: within one recursion level, a run of equal values may
only be entered at its **first** element. Choosing the second `2` instead of
the first produces a subset already generated, character for character.
""",
        ),
        (
            "`i > start`, not `i > 0`",
            """
This is the line that decides the problem, and the wrong version passes the
first sample.

`i > 0` says "never pick a value equal to its predecessor anywhere", which
kills `[1,1]` outright — the second `1` is picked at depth 1, where `start`
is 1, so it is the *first* choice at that level and must be allowed through.
Every legitimate repeat lives on the branch where the previous copy was
already taken.

`i > start` says the narrower and correct thing: "not as a **sibling** of an
identical earlier choice". Siblings are the duplicates; descendants are not.

If you would rather not reason about indices, `Counter(nums)` and a loop over
distinct values taking 0..k copies of each is the same algorithm with the
invariant made explicit — a reasonable thing to offer if the interviewer looks
sceptical about the off-by-one.
""",
        ),
    ],
}


def subsets_with_dup(nums: list[int]) -> list[list[int]]:
    ordered = sorted(nums)  # a copy: equal values must be adjacent
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int) -> None:
        result.append(path[:])  # every node is an answer
        for i in range(start, len(ordered)):
            if i > start and ordered[i] == ordered[i - 1]:
                continue  # a sibling identical to the last choice: same subset
            path.append(ordered[i])
            explore(i + 1)
            path.pop()

    explore(0)
    return result


CASES = [
    (([1, 2, 2],), [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]),
    (([2, 1, 2],), [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]),
    (([2, 2, 2],), [[], [2], [2, 2], [2, 2, 2]]),
    (([-1, -1, 2],), [[], [-1], [-1, -1], [-1, -1, 2], [-1, 2], [2]]),
    (([0],), [[], [0]]),
    (([],), [[]]),
]


def solve(nums: list[int]) -> list[list[int]]:
    return subsets_with_dup(nums)
