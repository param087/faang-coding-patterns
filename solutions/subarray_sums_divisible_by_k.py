"""Subarray Sums Divisible by K — LeetCode 974."""

from __future__ import annotations

from collections import defaultdict

META = {
    "pattern": "prefix-sums",
    "insight": "Group prefix sums by remainder mod k; every pair inside a group brackets a divisible subarray, so count pairs.",
    "time": "O(n)",
    "space": "O(k)",
    "sections": [
        (
            "What it asks",
            """
Count the contiguous subarrays whose sum is divisible by `k`. Count, not find —
so the answer can be quadratic in size (`[0] * 3 * 10⁴` with `k = 1` gives
about 4.5 × 10⁸ subarrays) even though the algorithm is linear.

Ask: **can values be negative?** They can, and that is the only real trap here.
Also confirm `k >= 1`, so the modulus is defined.
""",
        ),
        (
            "The insight",
            """
`sum(l..r)` is divisible by `k` exactly when `prefix[r + 1] ≡ prefix[l]
(mod k)`. So bucket the `n + 1` prefix sums by remainder: any **two** prefixes
in the same bucket bracket a valid subarray, and every valid subarray arises
that way exactly once.

That makes the answer `Σ C(m, 2)` over bucket sizes `m`. You can compute it in
one pass without ever materialising the buckets: keep a counter of remainders
seen so far, and before recording the current remainder, add however many
earlier prefixes already share it.

```
count += seen[remainder]
seen[remainder] += 1
```

Seed `seen[0] = 1` for the empty prefix, or you lose every subarray that starts
at index 0.

Note the bookkeeping: this problem **counts occurrences**, where Contiguous
Array and Maximum Size Subarray Sum Equals k store the **first index**. Counting
versus longest is what decides which of the two you write, and it is worth
naming the distinction explicitly.
""",
        ),
        (
            "Negative numbers, which is the whole difficulty",
            """
`k` is positive, so remainders should live in `0 .. k - 1`. Python cooperates:
`-1 % 5 == 4`. C, C++, Java and Go do not — their `%` takes the sign of the
dividend, so `-1 % 5 == -1`, and `-1` and `4` land in different buckets even
though they are the same residue class. Half your subarrays vanish.

The fix is `((sum % k) + k) % k`. Write it even in Python if the interviewer is
a Java person; it costs one line and shows you know why it is there.

`[-1, -2, -3]` with `k = 3` is the case that exposes it: prefix sums
`0, -1, -3, -6` have residues `0, 2, 0, 0`, giving `1 + 2 = 3` subarrays
(`[-3]`, `[-1, -2]`, `[-1, -2, -3]`). A sign-naive implementation reports `1`.

One more, since it is easy to miss: **overflow**. In Java the count itself needs
no widening (it fits in `int` for n = 3 × 10⁴), but the running prefix sum does
not — values reach ±10⁴ across 3 × 10⁴ elements, which stays inside `int`, so
here you are fine. Check the arithmetic rather than reciting a rule.
""",
        ),
    ],
}


def subarrays_div_by_k(nums: list[int], k: int) -> int:
    # Remainder -> how many prefixes so far had it. The empty prefix counts.
    seen: defaultdict[int, int] = defaultdict(int)
    seen[0] = 1

    running = 0
    count = 0

    for value in nums:
        running += value
        # ((r % k) + k) % k in a language whose % follows the dividend's sign.
        remainder = running % k

        count += seen[remainder]  # pair with every earlier prefix in this bucket
        seen[remainder] += 1

    return count


CASES = [
    (([4, 5, 0, -2, -3, 1], 5), 7),
    (([-1, -2, -3], 3), 3),
    (([-1, 2, 9], 2), 2),
    (([2, -2, 2, -4], 6), 2),
    (([0, 0, 0], 1), 6),
    (([5], 5), 1),
    (([5], 9), 0),
    (([], 5), 0),
]


def solve(nums: list[int], k: int) -> int:
    return subarrays_div_by_k(nums, k)
