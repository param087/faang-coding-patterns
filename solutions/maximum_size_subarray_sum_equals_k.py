"""Maximum Size Subarray Sum Equals k — LeetCode 325 (Premium)."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "Store the earliest index for each prefix sum, then each position asks the map for prefix - k and takes the span.",
    "time": "O(n)",
    "space": "O(n)",
    "sections": [
        (
            "What it asks",
            """
Given an integer array and a target `k`, return the length of the **longest**
contiguous subarray summing to exactly `k`. Return `0` if there is none.

This one is LeetCode Premium, so the statement is not public — the task is as
described above, and it turns up at Facebook and Amazon as the harder sibling
of Subarray Sum Equals K.

Ask: **can the array contain negatives and zeros?** Yes to both, and that
single answer determines the whole solution. Also confirm *longest* rather than
*count* — the two versions share a skeleton but not their bookkeeping.
""",
        ),
        (
            "The insight",
            """
`sum(l..r) = prefix[r + 1] - prefix[l]`, so a subarray ending at `r` sums to
`k` exactly when some earlier prefix equals `prefix[r + 1] - k`.

Walk once, carrying the running sum. At each index look up `running - k` in a
map of prefix value → index; if it is there, you have found a valid subarray and
its length is the gap between the indices.

Two details make it correct:

- **Store the earliest index for each prefix value.** You want the longest span,
  so an entry is written once and never updated: `if running not in first: ...`.
  A later duplicate prefix can only produce a shorter subarray.
- **Seed with `{0: -1}`.** The empty prefix is `0` and it sits before index `0`.
  Without it, a subarray that starts at index `0` — `[1, 2, 3]` with `k = 6` —
  is never found.

Do the lookup **before** the insert. Otherwise `k = 0` matches the prefix you
just wrote and every position reports a subarray of length `0`.
""",
        ),
        (
            "Why not a sliding window",
            """
The reflex answer is a two-pointer window: extend right while the sum is below
`k`, shrink from the left while it is above. It is O(n), it needs no map, and it
is **wrong** here.

That window depends on the sum being monotonic in the window's width, which
holds only when every element is non-negative. With negatives, growing the
window can *decrease* the sum, so shrinking on an overshoot discards subarrays
that would have come back into range.

`[1, -1, 5, -2, 3]` with `k = 3` is the counterexample worth memorising. The
answer is `4` — the whole prefix `[1, -1, 5, -2]`. A sliding window sees the sum
reach `5` at index 2, shrinks from the left, and never recovers the span; it
reports `1` or `2` depending on how it is written.

State this explicitly when you present the solution. "Negatives are allowed, so
a sliding window does not apply, which is why I am using prefix sums plus a hash
map" is the sentence the interviewer is listening for — it is the same reason
Minimum Size Subarray Sum (209) *can* use a window and this cannot.
""",
        ),
    ],
}


def max_subarray_len(nums: list[int], k: int) -> int:
    # Prefix value -> earliest index. Index -1 stands for the empty prefix.
    first_seen = {0: -1}
    running = 0
    best = 0

    for i, value in enumerate(nums):
        running += value

        # Look up before inserting, or k == 0 matches the entry just written.
        if running - k in first_seen:
            best = max(best, i - first_seen[running - k])

        if running not in first_seen:
            first_seen[running] = i  # earliest only: we want the longest span

    return best


CASES = [
    (([1, -1, 5, -2, 3], 3), 4),
    (([-2, -1, 2, 1], 1), 2),
    (([1, 2, 3], 6), 3),
    (([1, 2, 3], 7), 0),
    (([1, 1, 0], 1), 2),
    (([0, 0, 0], 0), 3),
    (([-1, 1], 0), 2),
    (([5], 5), 1),
    (([], 0), 0),
]


def solve(nums: list[int], k: int) -> int:
    return max_subarray_len(nums, k)
