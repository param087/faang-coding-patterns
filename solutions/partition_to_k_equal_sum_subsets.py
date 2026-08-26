"""Partition to K Equal Sum Subsets — LeetCode 698."""

from __future__ import annotations

META = {
    "pattern": "backtracking",
    "insight": "Fill one bucket at a time to completion, and only ever let the largest unplaced number open a fresh bucket — buckets are interchangeable.",
    "time": "O(k · 2ⁿ) with memoisation, O(kⁿ) without; n ≤ 16 by construction",
    "space": "O(n) recursion depth",
    "sections": [
        (
            "What it asks",
            """
Split every number into exactly `k` non-empty groups of equal sum. Return a
boolean — you never have to produce the groups, which is what makes the
symmetry pruning below legal.

`n ≤ 16` and `k ≤ n` in the constraints. That is an explicit invitation to
exponential search over subsets, and a hint that a 2ⁿ bitmask DP is the intended
upper bound.

Ask whether values are positive. They are on LeetCode, and it matters: with
negatives, `total % k != 0` and `max > target` stop being valid rejections, and
the whole pruning scheme has to be thrown away.
""",
        ),
        (
            "The insight",
            """
There are two ways to shape the recursion and they are not equally good.

**Per-number:** for each number, choose which of the `k` buckets it goes in.
Branching `k`, depth `n` — up to 16¹⁶ before pruning.

**Per-bucket:** fill bucket 1 to exactly `target`, then start bucket 2 from
scratch, and so on. Branching is "which unused numbers complete this bucket",
and the moment a bucket hits `target` you commit to it and never revisit — a
completed bucket is a completed bucket, whatever the rest looks like.

Per-bucket is the version that prunes well, because of one observation:
**buckets are unlabelled**. Any solution can be relabelled, so when a bucket is
empty you may assume without loss of generality that it contains the largest
unplaced number. If the search fails with that number opening the bucket, it
fails outright — no other opener can rescue it. That is the

```python
if remaining == target:
    break
```

line, and it is doing more work than every other line in the function.

Two supporting prunes: sort descending so large numbers commit early, and skip a
value equal to its predecessor when the predecessor is unused — trying the
second `7` after the first `7` already failed explores an identical subtree.
""",
        ),
        (
            "Follow-ups and the DP alternative",
            """
- **`[10,10,10,7,7,7,7,7,7,6,6,6]`, `k = 3`** is the case to have ready. Target
  is 30 and greedy takes `10+10+10`, which strands the rest: the sevens and
  sixes cannot make 30 (`7a + 6b = 30` needs `a = 0, b = 5`, and there are only
  three sixes). The real answer is three copies of `10+7+7+6`, so this is
  **true** — and only search finds it.
- **`[2,2,2,2,3,4,5]`, `k = 4`.** Sum 20, target 5, no element exceeds 5, every
  cheap rejection passes — and it is still **false**, because the `4` needs a
  `1` that does not exist.
- **Bitmask DP.** `dp[mask]` = the fill of the bucket in progress after using the
  numbers in `mask`. Since `sum(mask) // target` tells you how many buckets are
  done, the state is the mask alone: O(2ⁿ · n) time, 65536 states at `n = 16`.
  Slower to write, but it is the answer when the interviewer asks for a
  worst-case bound rather than a heuristic.
- **Return the partition, not a bool.** The symmetry prune stays valid (any one
  witness suffices), but you now have to carry the assignment array, so plan for
  it before you start typing.
- **`k = 1`** is trivially true, and **`k > n`** is false because some group
  would be empty. Both are worth stating; graders test them.
""",
        ),
    ],
}


def can_partition_k_subsets(nums: list[int], k: int) -> bool:
    total = sum(nums)
    if k < 1 or len(nums) < k or total % k:
        return False

    target = total // k
    ordered = sorted(nums, reverse=True)  # commit the big values first
    if ordered[0] > target:
        return False

    n = len(ordered)
    used = [False] * n

    def fill(buckets_left: int, start: int, remaining: int) -> bool:
        if buckets_left == 0:
            return True
        if remaining == 0:  # this bucket is exactly full — commit and move on
            return fill(buckets_left - 1, 0, target)

        for i in range(start, n):
            if used[i] or ordered[i] > remaining:
                continue
            # An equal value whose twin is still unused gives an identical subtree.
            if i > 0 and ordered[i] == ordered[i - 1] and not used[i - 1]:
                continue

            used[i] = True
            if fill(buckets_left, i + 1, remaining - ordered[i]):
                return True
            used[i] = False

            if remaining == target:
                # Failed with the largest unplaced value opening an empty bucket.
                # Buckets are unlabelled, so no other opener can succeed either.
                break

        return False

    return fill(k, 0, target)


CASES = [
    (([4, 3, 2, 3, 5, 2, 1], 4), True),
    (([1, 2, 3, 4], 3), False),  # sum 10 is not divisible by 3
    (([2, 2, 2, 2, 3, 4, 5], 4), False),  # divisible, all fit, still impossible
    (([10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], 3), True),  # greedy fails here
    (([1, 1, 1, 1], 4), True),
    (([4], 1), True),
    (([1, 2], 3), False),  # k > n, so some group would be empty
    (([], 3), False),
]


def solve(nums: list[int], k: int) -> bool:
    return can_partition_k_subsets(nums, k)
