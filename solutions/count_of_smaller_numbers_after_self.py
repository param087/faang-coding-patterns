"""Count of Smaller Numbers After Self — LeetCode 315."""

from __future__ import annotations

META = {
    "pattern": "divide-and-conquer",
    "insight": "Merge sort splits every pair exactly once; charge each left element the right-half values already emitted ahead of it.",
    "time": "O(n log n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
For each position, how many values **strictly smaller** sit to its right.
Return one count per index, in the original index order.

Two clarifications are worth a sentence each, because both change the code:
**strictly** smaller (equal values must not be counted), and the answers come
back **per original index**, not per sorted position. The second is what
forces you to carry indices through the sort.
""",
        ),
        (
            "Brute force, and why it fails",
            """
Two nested loops: for each `i`, scan `j > i`. That is n²/2 comparisons, and
the constraint is n ≤ 10⁵ — **5 × 10⁹ comparisons**, minutes of runtime
against a one-second limit. This is the rare problem where the quadratic
version is not a stepping stone you might get away with; it is a timeout on
the sample constraints.

A sorted-list insertion (`bisect.insort` scanning right to left) *looks*
linearithmic but `insort` shifts memory, so it is O(n²) byte moves. It passes
on LeetCode because memmove is fast, and it is a terrible thing to claim as
O(n log n) out loud. Say "O(n²) moves that happen to be cheap" if you offer
it.
""",
        ),
        (
            "The insight",
            """
Count **inversions**, and let merge sort do the counting.

A pair `(i, j)` with `i < j` and `nums[i] > nums[j]` is split by exactly one
merge step in the whole recursion — the one where `i` lands in the left half
and `j` in the right. So if every merge charges the pairs it separates, the
totals add up to the answer with no double counting.

During a merge, when you emit a left-half element, `j` right-half elements
have already been emitted. Every one of them was smaller *and* started to the
right of it, so:

```
counts[left[i]] += j
```

That single line is the whole algorithm. Everything else is standard merge
sort.
""",
        ),
        (
            "Sort indices, not values",
            """
The counts are keyed by **original index**, but the sort permutes values. Two
equal values would become indistinguishable, and you would have no way to
attribute a count.

So sort a list of indices, comparing by `nums[index]`. The merge moves indices
around; `counts` stays in original-index order and is written through the
index. This is the same discipline as storing indices on a monotonic stack.

The second decision is the tie-break: take from the left when

```
nums[left[i]] <= nums[right[j]]
```

with `<=`, not `<`. Ties must be emitted from the left first, so that equal
right-half elements are *not* yet counted in `j`. Flip that to `<` and equal
values get counted as "smaller" — the bug that `[1, 1, 0, 1]` catches and
`[5, 2, 6, 1]` does not.
""",
        ),
        (
            "Dry run",
            """
`[5, 2, 6, 1]` (as indices `[0, 1, 2, 3]`).

- Left half `[5, 2]`: merging, `2` is emitted first from the right, then `5`
  is emitted with `j = 1` → `counts[0] = 1`. Sorted: `[2, 5]`.
- Right half `[6, 1]`: `1` first, then `6` with `j = 1` → `counts[2] = 1`.
  Sorted: `[1, 6]`.
- Final merge of `[2, 5]` and `[1, 6]`: `1` goes out first, so `j = 1`. Then
  `2` (index 1) is emitted with `j = 1` → `counts[1] = 1`, then `5` (index 0)
  with `j = 1` → `counts[0] += 1 = 2`, then `6`.

Result `[2, 1, 1, 0]`. Note index 0 collected its count across **two different
levels** — one for the `2` beside it, one for the `1` two places away. That is
the part people get wrong when they try to finish each answer in one place.
""",
        ),
        (
            "Follow-ups",
            """
- **Fenwick tree instead**: coordinate-compress the values, then sweep right
  to left doing `query(rank - 1)` and `update(rank)`. Same O(n log n), easier
  to adapt to "count of greater", and the answer to ask for when the array
  arrives as a stream.
- **Reverse Pairs** (LeetCode 493) changes the predicate to `a > 2b`. The same
  skeleton, but the count no longer falls out of the merge comparison — it
  needs a separate two-pointer pass per merge.
- **Count of Range Sum** (LeetCode 327) is this algorithm run over the prefix
  sums with a two-sided window instead of a single pointer.
- **Count of greater after self**: mirror the tie-break (`<` becomes the
  strict side) rather than negating the array — negation quietly breaks on
  `INT_MIN` in languages with fixed-width ints.
""",
        ),
    ],
}


def count_smaller(nums: list[int]) -> list[int]:
    counts = [0] * len(nums)

    def sort(indices: list[int]) -> list[int]:
        if len(indices) <= 1:
            return indices

        mid = len(indices) // 2
        left, right = sort(indices[:mid]), sort(indices[mid:])

        merged: list[int] = []
        i = j = 0
        while i < len(left) or j < len(right):
            # `<=` keeps the merge stable, so equal values are never counted.
            take_left = j == len(right) or (i < len(left) and nums[left[i]] <= nums[right[j]])
            if take_left:
                counts[left[i]] += j  # j right-half values already emitted, all smaller
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        return merged

    sort(list(range(len(nums))))
    return counts


CASES = [
    (([5, 2, 6, 1],), [2, 1, 1, 0]),
    (([-1],), [0]),
    (([-1, -1],), [0, 0]),
    (([],), []),
    (([1, 2, 3, 4],), [0, 0, 0, 0]),
    (([4, 3, 2, 1],), [3, 2, 1, 0]),
    # Equal values must not count as smaller. Flipping the merge tie-break to a
    # strict `<` returns [3, 2, 0, 0] here — every equal value counted as smaller.
    (([1, 1, 0, 1],), [1, 1, 0, 0]),
    (([-2, 3, -1, 0],), [0, 2, 0, 0]),
]


def solve(nums: list[int]) -> list[int]:
    return count_smaller(list(nums))
