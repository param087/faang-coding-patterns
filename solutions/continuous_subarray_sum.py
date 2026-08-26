"""Continuous Subarray Sum — LeetCode 523."""

from __future__ import annotations

META = {
    "pattern": "prefix-sums",
    "insight": "A subarray sums to a multiple of k exactly when its two enclosing prefix sums share a remainder mod k.",
    "time": "O(n)",
    "space": "O(min(n, k))",
    "sections": [
        (
            "What it asks",
            """
Does the array contain a contiguous subarray of length **at least two** whose
sum is a multiple of `k`? Return a boolean.

Ask three things, because each one changes the code:

- **Does `0` count as a multiple of `k`?** Yes. `[0, 0]` is `True` for every
  `k`, and forgetting this is the fastest way to fail the hidden tests.
- **Length at least two** — confirm it out loud, because the whole difference
  between this and a one-liner is that constraint.
- **Can `k` be `0`?** Current constraints say `k >= 1`, but the problem shipped
  for years allowing `0`, and interviewers still ask. With `k = 0` the question
  becomes "two or more consecutive elements summing to `0`".
""",
        ),
        (
            "The insight",
            """
`sum(l..r) = prefix[r + 1] - prefix[l]`, so that sum is divisible by `k` exactly
when

```
prefix[r + 1] ≡ prefix[l]   (mod k)
```

Two prefix sums with the **same remainder** bracket a subarray that is a
multiple of `k`. So you never store sums — you store remainders, and there are
at most `k` of them, which is where the `O(min(n, k))` space comes from.

Keep a map from remainder to the **earliest index** at which it appeared, seeded
with `{0: -1}` for the empty prefix. When the current remainder is already in
the map, you have a candidate; check its length and you are done.
""",
        ),
        (
            "The two traps",
            """
**Length ≥ 2 means you compare indices, not membership.** A remainder that
first appeared at index `i - 1` gives a subarray of length 1, which does not
count. The test is `i - first[r] >= 2`, and the consequence is that on a hit you
must **not** overwrite the stored index — the earliest occurrence is the only
one that can ever produce a long enough gap.

`[5, 0]` with `k = 5` is the case that separates the two mistakes. Remainder `0`
is seeded at `-1`; at `i = 0` the running remainder is `0` again but the gap is
`0 - (-1) = 1`, too short. If you overwrote the entry with `0` there, then at
`i = 1` the gap is `1 - 0 = 1` and you wrongly return `False`. Leave it alone
and the gap is `1 - (-1) = 2` → `True`, which is right: `5 + 0 = 5`.

**Negative remainders.** Python's `%` already returns a non-negative result for
positive `k`, so `-3 % 5 == 2` and nothing needs fixing. In Java or C++, `%`
follows the sign of the dividend and you must normalise with
`((r % k) + k) % k`. Say this even in a Python round — it is the difference
between having used the trick and having memorised it.
""",
        ),
    ],
}


def check_subarray_sum(nums: list[int], k: int) -> bool:
    # Remainder -> earliest index. The empty prefix has remainder 0 at index -1.
    first_seen = {0: -1}
    running = 0

    for i, value in enumerate(nums):
        running += value
        # k == 0 has no modulus; the condition degenerates to "sums to zero".
        remainder = running % k if k else running

        if remainder in first_seen:
            if i - first_seen[remainder] >= 2:  # length at least two
                return True
            # Do not overwrite: only the earliest index can span far enough.
        else:
            first_seen[remainder] = i

    return False


CASES = [
    (([23, 2, 4, 6, 7], 6), True),
    (([23, 2, 6, 4, 7], 6), True),
    (([23, 2, 6, 4, 7], 13), False),
    (([5, 0], 5), True),
    (([6], 6), False),
    (([0, 0], 7), True),
    (([1, 2, 12], 6), False),
    (([1, 0, 0, 2], 0), True),
    (([1, 0, 2], 0), False),
]


def solve(nums: list[int], k: int) -> bool:
    return check_subarray_sum(nums, k)
