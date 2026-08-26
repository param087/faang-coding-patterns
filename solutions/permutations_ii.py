"""Permutations II — LeetCode 47."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Among equal values, force the copies to be used left to right: skip a value whose identical predecessor is still unused.",
    "time": "O(n · n!) worst case, far less when duplicates are dense",
    "space": "O(n) for the recursion and the used-array, excluding the output",
    "sections": [
        (
            "What it asks",
            """
Every **distinct** arrangement of a list that may contain repeats. `[1,1,2]`
has three, not six.

Ask what "distinct" means here: distinct by value, so the two `1`s are
interchangeable. That is the whole problem — the input has n! arrangements of
*positions* but only n!/∏(kᵢ!) arrangements of *values*, and you have to emit
the second number without generating the first.
""",
        ),
        (
            "The insight",
            """
Generating all n! and deduping with a set is correct and is the answer to
beat. It is also catastrophic on the case the tests care about: `[1]*10` has
one distinct permutation and 3.6 million position-permutations, so you do
3.6 million units of work to return a single list.

Prune instead. Sort so equal values are adjacent, and impose a canonical rule:
**among a run of equal values, the copies must be consumed left to right.**
Then each distinct arrangement corresponds to exactly one path in the tree.

```python
if used[i] or (i > 0 and nums[i] == nums[i - 1] and not used[i - 1]):
    continue
```

Read the second clause aloud: "this value equals its neighbour to the left, and
that neighbour is *not* currently in the path, so this copy would be jumping
the queue." Skip it.
""",
        ),
        (
            "`not used[i - 1]` versus `used[i - 1]`",
            """
Dropping the `not` is the famous variant, and the interesting fact is that it
is **also correct** — both versions return every distinct permutation exactly
once. Plenty of blog posts claim otherwise. What changes is how much of the
tree you walk.

- `not used[i - 1]` consumes a run left to right. The very first copy you may
  enter is index `p`; every sibling `p+1, p+2, …` is rejected **at the moment
  of choice**, before any recursion.
- `used[i - 1]` consumes a run right to left. But at the top of the run nothing
  is used yet, so *every* sibling looks legal and gets entered. Those branches
  are eventually strangled deeper down when the ordering constraint bites —
  after a lot of wasted descent.

Node counts, same input, same output:

| input | permutations | `not used[i-1]` | `used[i-1]` |
|---|---|---|---|
| `[1]*8` | 1 | **9** | 2781 |
| `[1,1,1,1,2,2,2,2]` | 70 | **251** | 4695 |

309× on the first. Reject before descending, not after — the same rule that
decides N-Queens.

If sorting is unacceptable because the input order carries meaning, the
equivalent statement is a **per-level `seen` set**: `if value in seen:
continue` inside the loop. No sort, prunes at the point of choice, and it reads
as what it is.
""",
        ),
    ],
}


def permute_unique(nums: list[int]) -> list[list[int]]:
    ordered = sorted(nums)  # a copy: equal values must be adjacent
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(ordered)

    def explore() -> None:
        if len(path) == len(ordered):
            result.append(path[:])
            return
        for i, value in enumerate(ordered):
            if used[i]:
                continue
            # An equal copy may only be used after its left neighbour.
            if i > 0 and value == ordered[i - 1] and not used[i - 1]:
                continue
            used[i] = True
            path.append(value)
            explore()
            path.pop()
            used[i] = False

    explore()
    return result


CASES = [
    (([1, 1, 2],), [[1, 1, 2], [1, 2, 1], [2, 1, 1]]),
    (
        ([2, 2, 1, 1],),
        [
            [1, 1, 2, 2],
            [1, 2, 1, 2],
            [1, 2, 2, 1],
            [2, 1, 1, 2],
            [2, 1, 2, 1],
            [2, 2, 1, 1],
        ],
    ),
    (([1, 2, 3],), [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
    (([1, 1, 1],), [[1, 1, 1]]),
    (([-1, -1],), [[-1, -1]]),
    (([3],), [[3]]),
    (([],), [[]]),
]


def solve(nums: list[int]) -> list[list[int]]:
    return permute_unique(nums)
