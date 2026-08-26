"""Contiguous Array — LeetCode 525."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "Score 0 as -1 and 'equal counts of 0 and 1' becomes 'sums to zero', which is just two equal prefix sums.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given a binary array, return the length of the longest contiguous subarray
containing an equal number of `0`s and `1`s.

Ask: **length or the subarray itself?** (Length — but if they want the indices,
you store the endpoints alongside the max and nothing else changes.) Confirm
the values really are only `0` and `1`, because the trick below depends on it.

Note the answer is always even, and `0` when no such subarray exists.
""",
        ),
        (
            "Brute force, and the number that kills it",
            """
Try every subarray, count zeros and ones. O(n³) naively, O(n²) if you extend
the counts incrementally.

Constraints go to n = 10⁵, so O(n²) is 10¹⁰ / 2 = **5 × 10⁹** count updates.
At a generous 10⁸ simple operations per second that is roughly a minute per
test case. Not close. You need one pass.
""",
        ),
        (
            "The insight",
            """
"Equal counts" is a balance condition, and balance conditions become **sums**
the moment you pick the right encoding. Score a `1` as `+1` and a `0` as `-1`.
Now:

> equal number of 0s and 1s in `nums[l..r]`  ⟺  `nums[l..r]` sums to 0

And a subarray sums to zero exactly when its two enclosing prefix sums are
**equal**. So the question collapses to: for each prefix value, how far apart
are its first and last occurrences?

One pass, a running counter, and a hash map from prefix value to the index
where that value was **first** seen. When the counter repeats a value you have
found a zero-sum subarray, and its length is the gap between the indices.

This re-encoding is the transferable part. The same move turns "equal numbers
of each of three symbols" into a tuple-valued prefix, and "twice as many 1s as
0s" into scoring `+1` and `-2`.
""",
        ),
        (
            "First occurrence only — and why the seed is -1",
            """
Two details decide whether this passes.

**Never overwrite an entry.** You want the *longest* span between two equal
prefix values, so the map must keep the **earliest** index for each value. The
line is `if running not in first: first[running] = i`, and getting it backwards
turns the answer into the shortest such subarray, which still passes `[0, 1]`
and fails everything real.

This is precisely where Subarray Sum Equals K differs: that problem **counts**
subarrays, so it keeps a running tally of every occurrence and increments. Same
prefix-sum skeleton, opposite bookkeeping. Interviewers ask both, and mixing
them up is the classic failure.

**Seed the map with `{0: -1}`.** A subarray that starts at index 0 is balanced
when the prefix after it returns to `0` — but that `0` is the empty prefix,
which occurs *before* index 0. Recording it at the virtual index `-1` makes the
length come out as `i - (-1) = i + 1` with no special case. Skip the seed and
`[0, 1]` returns `0`.
""",
        ),
        (
            "Dry run",
            """
`[0, 0, 1, 0, 0, 0, 1, 1]`, scored as `[-1, -1, +1, -1, -1, -1, +1, +1]`.

| i | value | running | map action | length |
|---|-------|---------|-----------|--------|
| — | — | 0 | seed `0 → -1` | — |
| 0 | -1 | -1 | new, store `-1 → 0` | — |
| 1 | -1 | -2 | new, store `-2 → 1` | — |
| 2 | +1 | -1 | seen at 0 | 2 - 0 = **2** |
| 3 | -1 | -2 | seen at 1 | 3 - 1 = 2 |
| 4 | -1 | -3 | new, store `-3 → 4` | — |
| 5 | -1 | -4 | new, store `-4 → 5` | — |
| 6 | +1 | -3 | seen at 4 | 6 - 4 = 2 |
| 7 | +1 | -2 | seen at **1** | 7 - 1 = **6** |

Answer `6`, the subarray `[1, 0, 0, 0, 1, 1]` at indices 1..6. That final row is
the one that catches an implementation which overwrote `-2 → 3` at step 3: it
would report `7 - 3 = 4`.
""",
        ),
        (
            "Follow-ups",
            """
- **Subarray Sum Equals K (560)** — count instead of longest, so the map holds
  occurrence counts and you add `counts[running - k]` before inserting.
- **Maximum Size Subarray Sum Equals k (325)** — the same first-occurrence map,
  with the target as a general `k` rather than `0`.
- **Equal 0s, 1s and 2s** — key the map on the *pair* of differences
  `(count0 - count1, count1 - count2)`. Two independent balances, one tuple.
- **"Twice as many 1s as 0s"** — score `0` as `-2` and `1` as `+1`; the map is
  unchanged. Being able to re-derive the scoring on the spot is the point.
- **Space** — the map holds at most `n + 1` distinct values, and the running
  sum is bounded by `±n`, so an array of size `2n + 1` offset by `n` replaces
  the hash map and removes the hashing constant.
""",
        ),
    ],
}


def find_max_length(nums: list[int]) -> int:
    # Prefix value -> earliest index where it appeared. The seed is the empty
    # prefix, which sits at the virtual index -1.
    first_seen = {0: -1}
    running = 0
    best = 0

    for i, value in enumerate(nums):
        running += 1 if value == 1 else -1  # 0 scores as -1

        if running in first_seen:
            best = max(best, i - first_seen[running])
        else:
            first_seen[running] = i  # earliest only: we want the longest span

    return best


CASES = [
    (([0, 1],), 2),
    (([0, 1, 0],), 2),
    (([0, 0, 1, 0, 0, 0, 1, 1],), 6),
    (([0, 1, 1, 0, 1, 1, 1, 0],), 4),
    (([1, 0, 1, 0, 1, 0],), 6),
    (([1, 1, 1, 0],), 2),
    (([0, 0, 0],), 0),
    (([1],), 0),
    (([],), 0),
]


def solve(nums: list[int]) -> int:
    return find_max_length(nums)
