"""Combination Sum II — LeetCode 40."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Two different jobs for one sort: `i + 1` spends each element once, and skipping equal siblings stops the same multiset repeating.",
    "time": "O(n · 2ⁿ) worst case",
    "space": "O(n) recursion depth, excluding the output",
    "sections": [
        (
            "What it asks",
            """
`candidates` may contain **duplicates**, every element may be used **at most
once** (by position), and the output must contain no duplicate combinations.
Return all of them summing to `target`.

The one clarification that matters: "used once" means once *per occurrence*, so
an input with two `1`s can legitimately produce `[1, 1, 6]`. Candidates are
positive, so the recursion terminates on a strictly shrinking remainder.
""",
        ),
        (
            "The insight",
            """
Sorting does two unrelated jobs here, and separating them is the answer.

**Job one — each element once.** Recurse on `i + 1`, so position `i` can never
be revisited. That alone is Combination Sum with the reuse taken away.

**Job two — no duplicate combinations.** With `[1, 1, 2, 5, 6, 7, 10]`, taking
the first `1` or the second `1` at the same depth yields the identical
multiset. Sorting puts equal values next to each other so "identical sibling"
becomes "equal to the previous index", and one line kills it:

```python
if i > start and candidates[i] == candidates[i - 1]:
    continue
```

Then keep the `break` on `candidates[i] > remaining` that the sort also buys
you: ascending order means one candidate being too large condemns the rest of
the loop.
""",
        ),
        (
            "Why `i > start` and not a global set",
            """
Deduping at the end with `set(map(tuple, result))` is the answer most people
reach for first. It is correct and it is a trap: on `[1] * 100` with
`target = 3` it enumerates C(100,3) ≈ 161 700 identical triples to return one.
The sibling skip never generates the second one at all.

`i > start` again, not `i > 0`. The first occurrence at each level must be
allowed through — the second `1` of `[1, 1, 6]` is chosen at a depth where
`start` already points at it, so it is that level's first choice, not a
repeated sibling. Getting this wrong loses every answer that legitimately
contains a repeated value, and the LeetCode sample `[10,1,2,7,6,1,5]` catches
it because `[1, 1, 6]` is one of the four expected answers.

Contrast with problem 39, where the recursive call passes `i`: there the sort
was purely an optimisation, here it is load-bearing for correctness.
""",
        ),
    ],
}


def combination_sum2(candidates: list[int], target: int) -> list[list[int]]:
    ordered = sorted(candidates)  # a copy: equal values must be adjacent
    result: list[list[int]] = []
    path: list[int] = []

    def explore(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(ordered)):
            if i > start and ordered[i] == ordered[i - 1]:
                continue  # identical sibling: same multiset, already emitted
            if ordered[i] > remaining:
                break  # ascending: nothing later fits either
            path.append(ordered[i])
            explore(i + 1, remaining - ordered[i])  # each position spent once
            path.pop()

    explore(0, target)
    return result


CASES = [
    (([10, 1, 2, 7, 6, 1, 5], 8), [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]),
    (([2, 5, 2, 1, 2], 5), [[1, 2, 2], [5]]),
    (([1, 1], 2), [[1, 1]]),
    (([1, 1], 1), [[1]]),
    (([3, 3, 3], 3), [[3]]),
    (([2, 3, 5], 1), []),
    (([], 3), []),
]


def solve(candidates: list[int], target: int) -> list[list[int]]:
    return combination_sum2(candidates, target)
